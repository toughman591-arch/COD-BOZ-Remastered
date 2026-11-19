.class public final Lcom/activision/boz/Immersive;
.super Ljava/lang/Object;

# Full screen: hide status + navigation bars (sticky immersive) and draw into the camera cutout (Android 9+).

.method public static apply(Landroid/app/Activity;)V
    .locals 4
    :try_start_0
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v0
    if-eqz v0, :cond_end
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I
    const/16 v2, 0x1c
    if-lt v1, v2, :cond_ui
    invoke-virtual {v0}, Landroid/view/Window;->getAttributes()Landroid/view/WindowManager$LayoutParams;
    move-result-object v2
    iget v3, v2, Landroid/view/WindowManager$LayoutParams;->layoutInDisplayCutoutMode:I
    const/4 v1, 0x1
    if-eq v3, v1, :cond_ui
    iput v1, v2, Landroid/view/WindowManager$LayoutParams;->layoutInDisplayCutoutMode:I
    invoke-virtual {v0, v2}, Landroid/view/Window;->setAttributes(Landroid/view/WindowManager$LayoutParams;)V
    :cond_ui
    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;
    move-result-object v0
    if-eqz v0, :cond_end
    const/16 v1, 0x1706
    invoke-virtual {v0, v1}, Landroid/view/View;->setSystemUiVisibility(I)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0
    :cond_end
    return-void
    :catch_0
    move-exception v0
    return-void
.end method
