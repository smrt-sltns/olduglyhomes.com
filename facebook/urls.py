from django.urls import path
from . import views2, views, myads, confirm_email, home, token_expired


urlpatterns = [
    # home
    path("", home.home, name="home"),
    path("login/", home.login, name="login"),
    path("user-logout", home.user_logout, name="user-logout"), 

    #myads
    path("adsets/<account_id>/<access_token>", myads.adset_list, name="adset-list"),
    path('adsets/<campaign_id>/valid-access/', myads.adset_list_campaign, name="adset-list-campaign"),
    path("set-ad-accounts/", myads.set_accountad, name="set-accountad"),
    path('sentiment-graph/<adset_id>/', myads.sentiment_graph, name='sentiment-graph' ),
    path("hide_comments/<adset_id>", myads.Hide_comment, name="hide-comment"),
    path("hide_comments/<adset_id>/<comment_id>/", myads.Hide_comment, name="hide-comment"),
    path("unhide_comments/<adset_id>", myads.Unhide_comment, name="unhide-comment"),
    path("unhide_comments/<adset_id>/<comment_id>/", myads.Unhide_comment, name="unhide-comment"),
    
    # views
    path("my-accounts/", views.get_accounts, name="account-list"),
    path("account-analysis/<account_id>/<account_access_token>", views.sentiment_graph_posts, name="sentiment-graph-post"),
    path("hide_comments/<account_id>/<account_access_token>", views.Post_hide_comment, name="post-hide-comment"),
    path("hide_comments/<account_id>/<comment_id>/<account_access_token>", views.Post_hide_comment, name="post-hide-comment"),
    path("unhide_comments/<account_id>/<account_access_token>", views.Post_unhide_comment, name="post-unhide-comment"),
    path("unhide_comments/<account_id>/<comment_id>/<account_access_token>", views.Post_unhide_comment, name="post-unhide-comment"),
    path("description", views.description, name='description'),

    #token expired 
    path("token-expired", token_expired.token_expired, name='token-expired'),
    path("token-expired-page", token_expired.token_expired_page, name="token-expired-page"),
    path("token-limit-reached", token_expired.token_limit_reached, name="token-limit-reached"),
    path("remove_old_access_token", token_expired.remove_old_access_token, name="remove-old-access-token"),

    # save credentials 
    path("save-app-creds/", views.save_app_credentials, name="save-app-credentials"),
    path("save-access-token/", views.save_access_token, name="save-access-token"),

    #confirm email 
    path("confirm-email/", confirm_email.confirm_email, name="confirm-email" ),

    #contact us 
    path("contact-us/", views.contact_us, name="contact_us"),

    # views2
    path('get-context2', views2.social_auth_data, name='get-context2'), 
    path('get-context3', views2.get_pages, name='get-context3'), 
    path('get_page_access_token', views2.get_post_and_comments_accounts, name='get-page-access-token'),
    path('get-account-posts/<page_id>/<page_access_token>',views2.get_posts, name='get-posts'),
    path('get-context', views2.user_social_data, name='get-context'),

]

