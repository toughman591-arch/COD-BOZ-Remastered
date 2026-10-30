.class public Lcom/activision/boz/Unpack$Ui;
.super Ljava/lang/Object;
.source "Unpack.java"

# interfaces
.implements Ljava/lang/Runnable;


# static fields
.field public static err:Ljava/lang/String;


# instance fields
.field public final act:Lcom/activision/boz/Unpack;

.field public final pct:I


# direct methods
.method public constructor <init>(Lcom/activision/boz/Unpack;I)V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/activision/boz/Unpack$Ui;->act:Lcom/activision/boz/Unpack;

    iput p2, p0, Lcom/activision/boz/Unpack$Ui;->pct:I

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    iget-object v0, p0, Lcom/activision/boz/Unpack$Ui;->act:Lcom/activision/boz/Unpack;

    iget v1, p0, Lcom/activision/boz/Unpack$Ui;->pct:I

    const/16 v2, 0x65

    if-ne v1, v2, :cond_0

    invoke-virtual {v0}, Lcom/activision/boz/Unpack;->launchMain()V

    return-void

    :cond_0
    iget-object v2, v0, Lcom/activision/boz/Unpack;->tv:Landroid/widget/TextView;

    if-eqz v2, :cond_2

    if-gez v1, :cond_1

    new-instance v3, Ljava/lang/StringBuilder;

    const-string v0, "Could not unpack the game data (v5.29 Mule Kick TEST 3 Mali).\n\nScreenshot this and send it:\n"

    invoke-direct {v3, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    sget-object v0, Lcom/activision/boz/Unpack$Ui;->err:Ljava/lang/String;

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    return-void

    :cond_1
    new-instance v3, Ljava/lang/StringBuilder;

    const-string v0, "Kino BO1 Remaster v5.29 Mule Kick TEST 3 (Mali / all GPUs)\n\nUnpacking game data (first launch only)\n\n"

    invoke-direct {v3, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string v0, "%"

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v2, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :cond_2
    return-void
.end method
