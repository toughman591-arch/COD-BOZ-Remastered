.class public Lcom/activision/boz/Unpack$Worker;
.super Ljava/lang/Object;
.source "Unpack.java"

# interfaces
.implements Ljava/lang/Runnable;


# instance fields
.field public final act:Lcom/activision/boz/Unpack;


# direct methods
.method public constructor <init>(Lcom/activision/boz/Unpack;)V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/activision/boz/Unpack$Worker;->act:Lcom/activision/boz/Unpack;

    return-void
.end method


# virtual methods
.method public run()V
    .locals 14

    iget-object v0, p0, Lcom/activision/boz/Unpack$Worker;->act:Lcom/activision/boz/Unpack;

    :try_start_0
    invoke-virtual {v0}, Landroid/content/Context;->getObbDir()Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->mkdirs()Z

    new-instance v2, Ljava/io/File;

    const-string v3, "blackops_atitc.dz.part"

    invoke-direct {v2, v1, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->delete()Z

    new-instance v3, Ljava/io/File;

    const-string v4, "blackops_etc.dz"

    invoke-direct {v3, v1, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->delete()Z

    new-instance v3, Ljava/io/File;

    const-string v4, "blackops_etc.dz.dat"

    invoke-direct {v3, v1, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->delete()Z

    invoke-static {v0}, Lcom/activision/boz/Unpack;->dzFile(Landroid/content/Context;)Ljava/io/File;

    move-result-object v3

    invoke-virtual {v3}, Ljava/io/File;->delete()Z

    invoke-virtual {v0}, Landroid/content/Context;->getAssets()Landroid/content/res/AssetManager;

    move-result-object v3

    const-string v4, "blackops_atitc.dz.xz"

    invoke-virtual {v3, v4}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object v3

    new-instance v4, Ljava/io/BufferedInputStream;

    const/high16 v5, 0x10000

    invoke-direct {v4, v3, v5}, Ljava/io/BufferedInputStream;-><init>(Ljava/io/InputStream;I)V

    new-instance v3, Lorg/tukaani/xz/XZInputStream;

    invoke-direct {v3, v4}, Lorg/tukaani/xz/XZInputStream;-><init>(Ljava/io/InputStream;)V

    new-instance v4, Ljava/io/FileOutputStream;

    invoke-direct {v4, v2}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V

    const/high16 v5, 0x100000

    new-array v5, v5, [B

    const-wide/16 v6, 0x0

    const/4 v8, -0x1

    :cond_0
    :goto_0
    invoke-virtual {v3, v5}, Ljava/io/InputStream;->read([B)I

    move-result v9

    if-ltz v9, :cond_1

    const/4 v10, 0x0

    invoke-virtual {v4, v5, v10, v9}, Ljava/io/FileOutputStream;->write([BII)V

    int-to-long v10, v9

    add-long/2addr v6, v10

    const-wide/16 v10, 0x64

    mul-long v10, v6, v10

    const-wide v12, 0x2082262eL

    div-long/2addr v10, v12

    long-to-int v10, v10

    if-eq v10, v8, :cond_0

    move v8, v10

    new-instance v11, Lcom/activision/boz/Unpack$Ui;

    invoke-direct {v11, v0, v10}, Lcom/activision/boz/Unpack$Ui;-><init>(Lcom/activision/boz/Unpack;I)V

    invoke-virtual {v0, v11}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    goto :goto_0

    :cond_1
    invoke-virtual {v4}, Ljava/io/FileOutputStream;->close()V

    invoke-virtual {v3}, Ljava/io/InputStream;->close()V

    const-wide v12, 0x2082262eL

    cmp-long v9, v6, v12

    if-eqz v9, :cond_2

    new-instance v1, Ljava/io/IOException;

    const-string v3, "size mismatch"

    invoke-direct {v1, v3}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    :cond_2
    invoke-static {v0}, Lcom/activision/boz/Unpack;->dzFile(Landroid/content/Context;)Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->delete()Z

    invoke-virtual {v2, v1}, Ljava/io/File;->renameTo(Ljava/io/File;)Z

    move-result v9

    if-nez v9, :cond_3

    new-instance v1, Ljava/io/IOException;

    const-string v3, "rename failed"

    invoke-direct {v1, v3}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1

    :cond_3
    new-instance v1, Ljava/io/File;

    invoke-virtual {v0}, Landroid/content/Context;->getObbDir()Ljava/io/File;

    move-result-object v2

    const-string v3, "kino_remaster_mule3m.ok"

    invoke-direct {v1, v2, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->createNewFile()Z

    new-instance v11, Lcom/activision/boz/Unpack$Ui;

    const/16 v10, 0x65

    invoke-direct {v11, v0, v10}, Lcom/activision/boz/Unpack$Ui;-><init>(Lcom/activision/boz/Unpack;I)V

    invoke-virtual {v0, v11}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    return-void

    :catch_0
    move-exception v1

    const-string v2, "KinoUnpack"

    const-string v3, "unpack failed"

    invoke-static {v2, v3, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    invoke-virtual {v1}, Ljava/lang/Throwable;->toString()Ljava/lang/String;

    move-result-object v2

    sput-object v2, Lcom/activision/boz/Unpack$Ui;->err:Ljava/lang/String;

    new-instance v11, Lcom/activision/boz/Unpack$Ui;

    const/4 v10, -0x1

    invoke-direct {v11, v0, v10}, Lcom/activision/boz/Unpack$Ui;-><init>(Lcom/activision/boz/Unpack;I)V

    invoke-virtual {v0, v11}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    return-void
.end method
