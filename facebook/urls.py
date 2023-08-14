from django.urls import path
from . import views2, views, myads, confirm_email, home


urlpatterns = [
    # home
    path("", home.home, name="home"),
    path("login/", home.login, name="login"),
    path("user-logout", home.user_logout, name="user-logout"), 

    #myads
    path("adsets/<account_id>/<access_token>", myads.adset_list, name="adset-list"),
    path('adset/<campaign_id>/valid-access/', myads.adset_list_campaign, name="adset-list-campaign"),
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

    # save credentials 
    path("save-app-creds/", views.save_app_credentials, name="save-app-credentials"),
    path("save-access-token/", views.save_access_token, name="save-access-token"),

    #confirm email 
    path("confirm-email/", confirm_email.confirm_email, name="confirm-email" ),

    # test 
    path("table/", views.display_table, name="display-table"),

    # views2
    path('get-context2', views2.social_auth_data, name='get-context2'), 
    path('get-context3', views2.get_pages, name='get-context3'), 
    path('get_page_access_token', views2.get_post_and_comments_accounts, name='get-page-access-token'),
    path('get-account-posts/<page_id>/<page_access_token>',views2.get_posts, name='get-posts'),
    path('get-context', views2.user_social_data, name='get-context'),

]


# https://kokes.github.io/blog/2018/02/04/facebook-downloading.html