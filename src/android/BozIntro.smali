.class public final Lcom/ideaworks3d/marmalade/BozIntro;
.super Ljava/lang/Object;
.source "BozIntro.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/ideaworks3d/marmalade/BozIntro$Video;,
        Lcom/ideaworks3d/marmalade/BozIntro$KinoScreen;
    }
.end annotation


# static fields
.field static final SIZE_C:J = 0xb807L

.field static final SIZE_K:J = 0xb876L

.field static lastMode:I

.field static lastTime:J


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 29
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static cached(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/io/File;
    .locals 7
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .prologue
    .line 66
    invoke-virtual {p0}, Landroid/app/Activity;->getCacheDir()Ljava/io/File;

    move-result-object v1

    new-instance v0, Ljava/io/File;

    invoke-direct {v0, v1, p2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 67
    invoke-virtual {v0}, Ljava/io/File;->length()J

    move-result-wide v2

    const-wide/16 v4, 0x0

    cmp-long v2, v2, v4

    if-lez v2, :cond_0

    .line 76
    :goto_0
    return-object v0

    .line 68
    :cond_0
    new-instance v2, Ljava/io/File;

    const-string v3, "boz_intro_tmp"

    invoke-direct {v2, v1, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 69
    invoke-virtual {p0}, Landroid/app/Activity;->getAssets()Landroid/content/res/AssetManager;

    move-result-object v1

    invoke-virtual {v1, p1}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object v1

    .line 70
    new-instance v3, Ljava/io/FileOutputStream;

    invoke-direct {v3, v2}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V

    .line 71
    const/high16 v4, 0x10000

    new-array v4, v4, [B

    .line 73
    :goto_1
    invoke-virtual {v1, v4}, Ljava/io/InputStream;->read([B)I

    move-result v5

    if-lez v5, :cond_1

    const/4 v6, 0x0

    invoke-virtual {v3, v4, v6, v5}, Ljava/io/FileOutputStream;->write([BII)V

    goto :goto_1

    .line 74
    :cond_1
    invoke-virtual {v3}, Ljava/io/FileOutputStream;->close()V

    invoke-virtual {v1}, Ljava/io/InputStream;->close()V

    .line 75
    invoke-virtual {v2, v0}, Ljava/io/File;->renameTo(Ljava/io/File;)Z

    goto :goto_0
.end method

.method static dp(Landroid/app/Activity;F)I
    .locals 2

    .prologue
    .line 93
    invoke-virtual {p0}, Landroid/app/Activity;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float/2addr v0, p1

    const/high16 v1, 0x3f000000    # 0.5f

    add-float/2addr v0, v1

    float-to-int v0, v0

    return v0
.end method

.method public static handle(Ljava/lang/String;IJJ)Z
    .locals 10

    .prologue
    const/4 v0, 0x0

    const/4 v1, 0x1

    .line 36
    if-nez p0, :cond_1

    .line 61
    :cond_0
    :goto_0
    return v0

    .line 38
    :cond_1
    const-wide/32 v2, 0xb807

    cmp-long v2, p4, v2

    if-eqz v2, :cond_2

    const-string v2, "boz_c.mp3"

    invoke-virtual {p0, v2}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_3

    :cond_2
    move v4, v1

    .line 40
    :goto_1
    if-eqz v4, :cond_0

    .line 41
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v6

    .line 42
    sget v2, Lcom/ideaworks3d/marmalade/BozIntro;->lastMode:I

    if-ne v4, v2, :cond_5

    sget-wide v2, Lcom/ideaworks3d/marmalade/BozIntro;->lastTime:J

    sub-long v2, v6, v2

    const-wide/16 v8, 0x7530

    cmp-long v2, v2, v8

    if-gez v2, :cond_5

    move v0, v1

    goto :goto_0

    .line 39
    :cond_3
    const-wide/32 v2, 0xb876

    cmp-long v2, p4, v2

    if-eqz v2, :cond_4

    const-string v2, "boz_k.mp3"

    invoke-virtual {p0, v2}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_9

    :cond_4
    const/4 v2, 0x2

    move v4, v2

    goto :goto_1

    .line 43
    :cond_5
    invoke-static {}, Landroid/os/Looper;->myLooper()Landroid/os/Looper;

    move-result-object v2

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v3

    if-eq v2, v3, :cond_0

    .line 45
    :try_start_0
    invoke-static {}, Lcom/ideaworks3d/marmalade/LoaderAPI;->getActivity()Lcom/ideaworks3d/marmalade/LoaderActivity;

    move-result-object v5

    .line 46
    if-eqz v5, :cond_0

    .line 47
    const/4 v2, 0x3

    if-ne v4, v2, :cond_notfive

    const-string v3, "intro/five_intro.mp4"

    const-string v2, "five_intro.mp4"

    goto :goto_3

    :cond_notfive
    if-ne v4, v1, :cond_6

    const-string v2, "intro/cotd_intro.mp4"

    move-object v3, v2

    :goto_2
    if-ne v4, v1, :cond_7

    const-string v2, "cotd_intro.mp4"

    :goto_3
    invoke-static {v5, v3, v2}, Lcom/ideaworks3d/marmalade/BozIntro;->cached(Landroid/app/Activity;Ljava/lang/String;Ljava/lang/String;)Ljava/io/File;

    move-result-object v2

    .line 48
    sput v4, Lcom/ideaworks3d/marmalade/BozIntro;->lastMode:I

    sput-wide v6, Lcom/ideaworks3d/marmalade/BozIntro;->lastTime:J

    .line 49
    const/4 v3, 0x3

    if-eq v4, v3, :cond_vid

    if-ne v4, v1, :cond_8

    :cond_vid

    .line 50
    new-instance v3, Ljava/util/concurrent/CountDownLatch;

    const/4 v4, 0x1

    invoke-direct {v3, v4}, Ljava/util/concurrent/CountDownLatch;-><init>(I)V

    .line 51
    new-instance v4, Lcom/ideaworks3d/marmalade/BozIntro$Video;

    invoke-virtual {v2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v4, v5, v2, v3}, Lcom/ideaworks3d/marmalade/BozIntro$Video;-><init>(Landroid/app/Activity;Ljava/lang/String;Ljava/util/concurrent/CountDownLatch;)V

    invoke-virtual {v5, v4}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 52
    const-wide/16 v4, 0xa0

    sget-object v2, Ljava/util/concurrent/TimeUnit;->SECONDS:Ljava/util/concurrent/TimeUnit;

    invoke-virtual {v3, v4, v5, v2}, Ljava/util/concurrent/CountDownLatch;->await(JLjava/util/concurrent/TimeUnit;)Z

    .line 58
    :goto_4
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v2

    sput-wide v2, Lcom/ideaworks3d/marmalade/BozIntro;->lastTime:J

    move v0, v1

    .line 59
    goto :goto_0

    .line 47
    :cond_6
    const-string v2, "intro/kino_loading.mp3"

    move-object v3, v2

    goto :goto_2

    :cond_7
    const-string v2, "kino_loading_515.mp3"

    goto :goto_3

    .line 54
    :cond_8
    new-instance v3, Ljava/util/concurrent/CountDownLatch;

    const/4 v4, 0x1

    invoke-direct {v3, v4}, Ljava/util/concurrent/CountDownLatch;-><init>(I)V

    .line 55
    new-instance v4, Lcom/ideaworks3d/marmalade/BozIntro$KinoScreen;

    invoke-virtual {v2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v4, v5, v2, v3}, Lcom/ideaworks3d/marmalade/BozIntro$KinoScreen;-><init>(Landroid/app/Activity;Ljava/lang/String;Ljava/util/concurrent/CountDownLatch;)V

    invoke-virtual {v5, v4}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 56
    const-wide/16 v4, 0x3c

    sget-object v2, Ljava/util/concurrent/TimeUnit;->SECONDS:Ljava/util/concurrent/TimeUnit;

    invoke-virtual {v3, v4, v5, v2}, Ljava/util/concurrent/CountDownLatch;->await(JLjava/util/concurrent/TimeUnit;)Z
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_4

    .line 60
    :catch_0
    move-exception v1

    goto/16 :goto_0

    :cond_9
    const-wide/32 v2, 0xb8e5

    cmp-long v2, p4, v2

    if-eqz v2, :cond_f3

    const-string v2, "boz_f.mp3"

    invoke-virtual {p0, v2}, Ljava/lang/String;->endsWith(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :cond_fnone

    :cond_f3
    const/4 v2, 0x3

    move v4, v2

    goto/16 :goto_1

    :cond_fnone
    move v4, v0

    goto/16 :goto_1
.end method

.method static label(Landroid/app/Activity;Ljava/lang/String;F)Landroid/widget/TextView;
    .locals 4

    .prologue
    const/4 v3, 0x0

    .line 84
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    .line 85
    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 86
    const/4 v1, -0x1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTextColor(I)V

    .line 87
    invoke-virtual {v0, p2}, Landroid/widget/TextView;->setTextSize(F)V

    .line 88
    sget-object v1, Landroid/graphics/Typeface;->DEFAULT_BOLD:Landroid/graphics/Typeface;

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V

    .line 89
    const/high16 v1, 0x40c00000    # 6.0f

    const/high16 v2, -0x1000000

    invoke-virtual {v0, v1, v3, v3, v2}, Landroid/widget/TextView;->setShadowLayer(FFFI)V

    .line 90
    return-object v0
.end method

.method static remove(Landroid/view/View;)V
    .locals 1

    .prologue
    .line 80
    if-eqz p0, :cond_0

    invoke-virtual {p0}, Landroid/view/View;->getParent()Landroid/view/ViewParent;

    move-result-object v0

    instance-of v0, v0, Landroid/view/ViewGroup;

    if-eqz v0, :cond_0

    invoke-virtual {p0}, Landroid/view/View;->getParent()Landroid/view/ViewParent;

    move-result-object v0

    check-cast v0, Landroid/view/ViewGroup;

    invoke-virtual {v0, p0}, Landroid/view/ViewGroup;->removeView(Landroid/view/View;)V

    .line 81
    :cond_0
    return-void
.end method
