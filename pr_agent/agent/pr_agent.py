import shlex

from pr_agent.algo.utils import update_settings_from_args
from pr_agent.config_loader import get_settings
from pr_agent.git_providers.utils import apply_repo_settings
from pr_agent.tools.pr_add_docs import PRAddDocs
from pr_agent.tools.pr_code_suggestions import PRCodeSuggestions
from pr_agent.tools.pr_config import PRConfig
from pr_agent.tools.pr_description import PRDescription
from pr_agent.tools.pr_information_from_user import PRInformationFromUser
from pr_agent.tools.pr_questions import PRQuestions
from pr_agent.tools.pr_reviewer import PRReviewer
from pr_agent.tools.pr_similar_issue import PRSimilarIssue
from pr_agent.tools.pr_update_changelog import PRUpdateChangelog

command2class = {
    "auto_review": PRReviewer,
    "answer": PRReviewer,
    "review": PRReviewer,
    "review_pr": PRReviewer,
    "reflect": PRInformationFromUser,
    "reflect_and_review": PRInformationFromUser,
    "describe": PRDescription,
    "describe_pr": PRDescription,
    "improve": PRCodeSuggestions,
    "improve_code": PRCodeSuggestions,
    "ask": PRQuestions,
    "ask_question": PRQuestions,
    "update_changelog": PRUpdateChangelog,
    "config": PRConfig,
    "settings": PRConfig,
    "similar_issue": PRSimilarIssue,
    "add_docs": PRAddDocs,
}

commands = list(command2class.keys())

class PRAgent:
    def __init__(self):
        pass

    async def handle_request(self, pr_url, request, notify=None) -> bool:
        # First, apply repo specific settings if exists
        apply_repo_settings(pr_url)

        # Then, apply user specific settings if exists
        request = request.replace("'", "\\'")
        lexer = shlex.shlex(request, posix=True)
        lexer.whitespace_split = True
        action, *args = list(lexer)
        args = update_settings_from_args(args)

        action = action.lstrip("/").lower()
        if action == "reflect_and_review":
            get_settings().pr_reviewer.ask_and_reflect = True
        if action == "answer":
            if notify:
                notify()
            await PRReviewer(pr_url, is_answer=True, args=args).run()
        elif action == "auto_review":
            await PRReviewer(pr_url, is_auto=True, args=args).run()
        elif action in command2class:
            if notify:
                notify()
            await command2class[action](pr_url, args=args).run()
        else:
            return False
        return True

