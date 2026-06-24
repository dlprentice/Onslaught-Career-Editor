/* address: 0x0046e460 */
/* name: CGame__Render */
/* signature: void __thiscall CGame__Render(void * this, int num_renders) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Source-aligned mapping to CGame::Render(SINT). Updates render-frame timing/fraction, configures
   split-screen/fullscreen viewports based on player count, calls engine pre/post render, renders
   viewpoints (0..3), then runs post-render HUD/overlay pipeline via FUN_0053ecc0 and
   reconnect-interface draws. */

void __thiscall CGame__Render(void *this,int num_renders)

{
  void *pvVar1;
  float fVar2;
  char cVar3;
  void *viewport;
  int iVar4;
  uint viewpoint;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  undefined4 local_2c;
  undefined4 local_28;
  int local_24;
  int local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d2958;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CMapWhoEntry__Init();
  local_4 = 0;
  fVar2 = (*(float *)((int)this + 0x3ac) * _DAT_005d8578 + DAT_00672fd0) * _DAT_005d8ba8;
  if (((((*(int *)((int)this + 0x2a0) < 0x352) || (899 < *(int *)((int)this + 0x2a0))) &&
       (DAT_009c648c != 0)) && ((DAT_0089c9b0 != 0 && (*(int *)(DAT_0089c9b0 + 0x14) != 0)))) &&
     (DAT_0089d680 == '\0')) {
    cVar3 = CDXLandscape__SetRenderTarget(*(undefined4 *)(DAT_0089c9b0 + 0x14));
    if (cVar3 != '\0') {
      DAT_0089d680 = '\x01';
      DAT_0083cd58 = 1;
    }
  }
  if (*(int *)((int)this + 0x38c) == -0x40800000) {
    *(undefined4 *)((int)this + 0x388) = 0x3f800000;
  }
  else {
    *(float *)((int)this + 0x388) = fVar2 - *(float *)((int)this + 0x38c);
  }
  *(float *)((int)this + 0x38c) = fVar2;
  do {
    if (DAT_0089d680 == '\0') {
      local_24 = PLATFORM__GetWindowWidth();
    }
    else {
      local_24 = 0x100;
    }
    if (DAT_0089d680 == '\0') {
      local_20 = PLATFORM__GetWindowHeight();
    }
    else {
      local_20 = 0x100;
    }
    local_1c = 0;
    local_18 = 0;
    local_14 = 0;
    local_10 = 0x3f800000;
    *(int *)((int)this + 0x14) = *(int *)((int)this + 0x14) + 1;
    *(uint *)((int)this + 0x390) = (uint)(num_renders == 0);
    if (*(int *)((int)this + 0x40) == 0) {
      iVar4 = *(int *)((int)this + 0x29c);
    }
    else {
      iVar4 = 1;
    }
    CEngine__SetNumViewpoints(&DAT_0089c9a0,iVar4);
    CDXEngine__PreRender(&DAT_0089c9a0,viewport);
    if (*(int *)((int)this + 0x300) == 0xff) goto LAB_0046e888;
    iVar4 = *(int *)((int)this + 0x29c);
    if ((iVar4 == 1) || (*(int *)((int)this + 0x40) != 0)) {
      local_3c = local_24;
      local_38 = local_20;
      local_34 = 0;
      local_30 = 0;
      local_2c = 0;
      local_28 = 0x3f800000;
      CConsole__Unk_0042d420();
      pvVar1 = *(void **)(*(int *)((int)this + 0x2a4) + 0x1c);
      if (pvVar1 != (void *)0x0) {
        CGame__Unk_00407540(pvVar1);
      }
      CEngine__SetViewpoint
                (&DAT_0089c9a0,0,*(void **)((int)this + 0x2c4),&local_3c,
                 *(void **)((int)this + 0x2a4));
      viewpoint = 0;
LAB_0046e87e:
      CDXEngine__Render(&DAT_0089c9a0,viewpoint);
    }
    else {
      if (iVar4 == 2) {
        if (*(char *)((int)this + 0x38) == '\0') {
          local_3c = local_24 / 2;
          local_38 = local_20;
        }
        else {
          local_3c = local_24;
          local_38 = local_20 / 2;
        }
        local_34 = 0;
        local_30 = 0;
        local_2c = 0;
        local_28 = 0x3f800000;
        CConsole__Unk_0042d420();
        pvVar1 = *(void **)(*(int *)((int)this + 0x2a4) + 0x1c);
        if (pvVar1 != (void *)0x0) {
          CGame__Unk_00407540(pvVar1);
        }
        pvVar1 = *(void **)(*(int *)((int)this + 0x2a8) + 0x1c);
        if (pvVar1 != (void *)0x0) {
          CGame__Unk_00407540(pvVar1);
        }
        CEngine__SetViewpoint
                  (&DAT_0089c9a0,0,*(void **)((int)this + 0x2c4),&local_3c,
                   *(void **)((int)this + 0x2a4));
        CDXEngine__Render(&DAT_0089c9a0,0);
        if (*(char *)((int)this + 0x38) == '\0') {
          local_34 = local_34 + local_24 / 2;
        }
        else {
          local_30 = local_30 + local_20 / 2;
        }
        CEngine__SetViewpoint
                  (&DAT_0089c9a0,1,*(void **)((int)this + 0x2c8),&local_3c,
                   *(void **)((int)this + 0x2a8));
        viewpoint = 1;
        goto LAB_0046e87e;
      }
      if ((iVar4 == 3) || (iVar4 == 4)) {
        local_34 = 0;
        local_3c = local_24 / 2;
        local_30 = 0;
        local_38 = local_20 / 2;
        local_2c = 0;
        local_28 = 0x3f800000;
        CEngine__SetViewpoint
                  (&DAT_0089c9a0,0,*(void **)((int)this + 0x2c4),&local_3c,
                   *(void **)((int)this + 0x2a4));
        CDXEngine__Render(&DAT_0089c9a0,0);
        local_34 = local_34 + local_24 / 2;
        CEngine__SetViewpoint
                  (&DAT_0089c9a0,1,*(void **)((int)this + 0x2c8),&local_3c,
                   *(void **)((int)this + 0x2a8));
        CDXEngine__Render(&DAT_0089c9a0,1);
        local_34 = local_34 - local_24 / 2;
        local_30 = local_30 + local_20 / 2;
        CEngine__SetViewpoint
                  (&DAT_0089c9a0,2,*(void **)((int)this + 0x2cc),&local_3c,
                   *(void **)((int)this + 0x2ac));
        CDXEngine__Render(&DAT_0089c9a0,2);
        if (*(int *)((int)this + 0x29c) == 4) {
          local_34 = local_34 + local_24 / 2;
          CEngine__SetViewpoint
                    (&DAT_0089c9a0,3,*(void **)((int)this + 0x2d0),&local_3c,
                     *(void **)((int)this + 0x2b0));
          viewpoint = 3;
          goto LAB_0046e87e;
        }
      }
    }
LAB_0046e888:
    CDXEngine__PostRender(&DAT_0089c9a0,&local_24);
    CVBufTexture__Unk_00527990();
    CVBufTexture__Unk_00527990();
    if (DAT_0089d680 == '\0') {
      local_4 = 0xffffffff;
      CDXLandscape__ReleaseSurfaces();
      ExceptionList = local_c;
      return;
    }
    DAT_0089d680 = '\0';
    DAT_0083cd58 = 0;
    CDXLandscape__ReleaseRenderTarget();
  } while( true );
}
