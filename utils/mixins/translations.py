# Translations
from utils import translations

# Decorador que sirve para darle las palabras traducidas a cada vista
class TranslationMixin:
    def dispatch(self, request, *args, **kwargs):
        """Return the normal dispatch but adds the list words translated."""

        url_name = self.get_url_name()
        if url_name:
            list_words = getattr(translations, f"{url_name}_translation")(self.request.global_context["language"])        
            self.list_words = list_words
        return super(TranslationMixin, self).dispatch(request, *args, **kwargs)

    def get_url_name(self):
        VIEWS_WITHOUT_TRANSLATION = ["CheckRecordsView", "CheckProfilesView", "AddEditDemonView", "AddEditProfileView", "LevelPacksView"]
        if self.__class__.__name__ == "DemonListView":
            url_name = "list"
        elif self.__class__.__name__ == "DemonDetailView":
            url_name = "level_detail"
        elif self.__class__.__name__ == "UserDetailView":
            url_name = "user_detail"
        elif self.__class__.__name__ in VIEWS_WITHOUT_TRANSLATION:
            url_name = None
        else:
            url_name = self.request.resolver_match.url_name
        return url_name
