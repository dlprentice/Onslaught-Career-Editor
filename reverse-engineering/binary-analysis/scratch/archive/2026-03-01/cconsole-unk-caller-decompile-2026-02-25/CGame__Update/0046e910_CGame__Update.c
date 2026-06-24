/* address: 0x0046e910 */
/* name: CGame__Update */
/* signature: void __fastcall CGame__Update(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Source-aligned mapping to CGame::Update(). Core gameplay tick/update path: dev-mode/easter-egg
   checks, controller/player updates, EventManager advance/flush cycle, atmosphere/map/audio-state
   transitions, pause/fade/game-state progression handling, and camera/control handoff logic. */

void __fastcall CGame__Update(void *this)

{
  float fVar1;
  bool bVar2;
  uint uVar3;
  void *pvVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  undefined *puVar8;
  int *piVar9;
  float fVar10;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  undefined4 local_4;

  iVar6 = 0;
  iVar5 = *(int *)((int)this + 0x18) + 1;
  *(int *)((int)this + 0x18) = iVar5;
  if (g_bDevModeEnabled == 0) goto switchD_0046e958_caseD_f1;
  uVar3 = iVar5 + DAT_00679ec8;
  if (uVar3 < 0x2775) {
    if (uVar3 != 0x2774) {
      switch(uVar3) {
      case 0xf0:
        CUnitAI__Unk_00441b10((void *)0x0,0);
        break;
      default:
        goto switchD_0046e958_caseD_f1;
      case 0x104:
      case 0x10e:
        goto switchD_0046e958_caseD_104;
      case 0x122:
switchD_0046e958_caseD_122:
        (**(code **)(**(int **)((int)this + 0x2f4) + 0xc))
                  (*(undefined4 *)((int)this + 0x2b4),0x33,0x3f800000);
        goto switchD_0046e958_caseD_f1;
      case 300:
switchD_0046e958_caseD_12c:
        (**(code **)(**(int **)(*(int *)((int)this + 0x2f4) + 8) + 0xc))
                  (*(undefined4 *)((int)this + 0x2b4),0x2b,0x3f800000);
        goto switchD_0046e958_caseD_f1;
      case 0x136:
        goto switchD_0046e958_caseD_136;
      }
    }
    (**(code **)(**(int **)((int)this + 0x2a4) + 0xc))
              (*(undefined4 *)((int)this + 0x2b4),0x38,0x3f800000);
  }
  else {
    if (0x27b0 < uVar3) {
      if (uVar3 != 0x27ba) {
        if (uVar3 == 0x4e84) {
          g_bDevModeEnabled = 0;
          g_bAllCheatsEnabled = 1;
        }
        goto switchD_0046e958_caseD_f1;
      }
switchD_0046e958_caseD_136:
      (**(code **)(**(int **)(*(int *)((int)this + 0x2f4) + 8) + 0xc))
                (*(undefined4 *)((int)this + 0x2b4),0x33,0x3f800000);
      DAT_00679ec8 = DAT_00679ec8 + 10000;
      goto switchD_0046e958_caseD_f1;
    }
    if (uVar3 == 0x27b0) goto switchD_0046e958_caseD_12c;
    if (uVar3 != 0x277e) {
      if (uVar3 != 0x27a6) goto switchD_0046e958_caseD_f1;
      local_c = 0x70;
      local_4 = 0x170;
      local_10 = 0xc0;
      local_8 = 0x1c0;
      CUnitAI__Unk_00441b10(&local_10,0);
      goto switchD_0046e958_caseD_122;
    }
  }
switchD_0046e958_caseD_104:
  (**(code **)(**(int **)((int)this + 0x2f4) + 0xc))
            (*(undefined4 *)((int)this + 0x2b4),0x2a,0x3f800000);
switchD_0046e958_caseD_f1:
  DAT_006605c8 = DAT_006605c8 + 1;
  CUnitAI__Unk_004b7d90();
  if (1 < *(int *)((int)this + 0x28)) {
    bVar2 = false;
    if (0 < *(int *)((int)this + 0x29c)) {
      puVar8 = &DAT_0089be50;
      piVar9 = (int *)((int)this + 0x2b4);
      do {
        if ((*piVar9 != 0) &&
           (iVar5 = CVBufTexture__Unk_00527c50(puVar8,*piVar9,(void *)0x1), (char)iVar5 != '\0')) {
          bVar2 = true;
        }
        iVar6 = iVar6 + 1;
        piVar9 = piVar9 + 1;
        puVar8 = puVar8 + 0xc;
      } while (iVar6 < *(int *)((int)this + 0x29c));
      if ((((bVar2) &&
           (pvVar4 = CController__GetToControl(*(void **)((int)this + 0x2b4)),
           pvVar4 == *(void **)((int)this + 0x2a4))) && (*(int *)((int)this + 0x2c) != 0)) &&
         (((DAT_0089be58 == 0 && (DAT_0089be64 == 0)) &&
          ((DAT_008a9d38 < 0x352 ||
           ((899 < DAT_008a9d38 ||
            (pvVar4 = CController__GetToControl(*(void **)((int)this + 0x2b8)),
            pvVar4 == *(void **)((int)this + 0x2a8))))))))) {
        *(undefined4 *)((int)this + 0x2c) = 0;
      }
    }
    _DAT_00854d90 = *(uint *)((int)this + 0x18) & 7;
  }
  if (((*(int *)((int)this + 0x2c) == 0) || (*(int *)((int)this + 0x9cc) == 1)) &&
     (DAT_00662dd4 == 0)) {
    CEventManager__AdvanceTime(&EVENT_MANAGER);
    CConsole__Unk_0042d4d0();
    iVar5 = 0;
    if (0 < *(int *)((int)this + 0x29c)) {
      piVar7 = &DAT_0066e8cc;
      piVar9 = (int *)((int)this + 0x2b4);
      do {
        if (*piVar9 != 0) {
          if (*(void **)(piVar9[-4] + 0x1c) != (void *)0x0) {
            iVar6 = CGame__IsWalkerGroundedOrCollision(*(void **)(piVar9[-4] + 0x1c));
            *piVar7 = iVar6;
          }
          (**(code **)(*(int *)*piVar9 + 8))();
        }
        iVar5 = iVar5 + 1;
        piVar7 = piVar7 + 1;
        piVar9 = piVar9 + 1;
      } while (iVar5 < *(int *)((int)this + 0x29c));
    }
    if (DAT_00679fc4 == '\0') {
      CController__Unk_0042da00(0);
    }
    CVBufTexture__Unk_00512470(0x855bb0);
    CEventManager__Flush(&EVENT_MANAGER);
    Atmospherics__RenderAll();
  }
  else if ((*(int *)((int)this + 0x28) < 10) && (iVar5 = 0, 0 < *(int *)((int)this + 0x29c))) {
    piVar9 = (int *)((int)this + 0x2b4);
    do {
      if ((int *)*piVar9 != (int *)0x0) {
        (**(code **)(*(int *)*piVar9 + 8))();
      }
      iVar5 = iVar5 + 1;
      piVar9 = piVar9 + 1;
    } while (iVar5 < *(int *)((int)this + 0x29c));
  }
  if ((*(int *)((int)this + 0x100) != 0) && (*(int *)((int)this + 0x2c) == 0)) {
    CSoundManager__Unk_004e1330(0x896988);
    *(undefined4 *)((int)this + 0x100) = 0;
  }
  if ((*(int *)((int)this + 0x100) == 0) && (*(int *)((int)this + 0x2c) == 1)) {
    CSoundManager__Unk_004e1300(0x896988);
    *(undefined4 *)((int)this + 0x100) = 1;
  }
  iVar5 = *(int *)((int)this + 0x28);
  *(undefined4 *)((int)this + 0x9cc) = 0;
  if ((iVar5 == 5) && (_DAT_005d856c <= *(float *)((int)this + 0x48))) {
    fVar10 = *(float *)((int)this + 0x48) - _DAT_005d8578;
    *(float *)((int)this + 0x48) = fVar10;
    if ((fVar10 <= _DAT_005d8578) &&
       ((DAT_0089be58 != 0 ||
        (((0x351 < DAT_008a9d38 && (DAT_008a9d38 < 900)) && (DAT_0089be64 != 0)))))) {
      *(undefined4 *)((int)this + 0x48) = 0x3d4ccccd;
    }
    if (((*(int *)((int)this + 0x30) == 0x2e5) || (*(int *)((int)this + 0x30) == 0x2e6)) ||
       (*(float *)((int)this + 0x48) < _DAT_005d856c)) {
      *(undefined4 *)((int)this + 0x34) = 1;
    }
  }
  if (((iVar5 == 4) || (iVar5 == 6)) || ((iVar5 == 7 || (iVar5 == 8)))) {
    if (*(float *)((int)this + 0x48) <= _DAT_005d8588) {
      if (*(int *)((int)this + 0x2c) == 0) {
        *(undefined4 *)((int)this + 0x394) = 1;
      }
    }
    else {
      fVar10 = PLATFORM__GetSysTimeFloat();
      if (((fVar10 <= _DAT_00679ecc) || (_DAT_005d85d8 <= fVar10 - _DAT_00679ecc)) ||
         (fVar1 = *(float *)((int)this + 0x48) - (fVar10 - _DAT_00679ecc), fVar1 <= _DAT_005dbbf4))
      {
        fVar1 = *(float *)((int)this + 0x48) - _DAT_005d8578;
      }
      *(float *)((int)this + 0x48) = fVar1;
      _DAT_00679ecc = fVar10;
    }
    if ((*(float *)((int)this + 0x48) <= _DAT_005d8bd8) && (DAT_00679fc4 == '\0')) {
      _DAT_00679fd4 = 0;
      _DAT_00679fd8 = 0;
      _DAT_00679fdc = 0;
      _DAT_00679fe8 = 0;
      DAT_00679fcc = 0;
      _DAT_00679fd0 = 0x46;
      if (*(int *)((int)this + 0x9d0) == 1) {
        if (1 < DAT_008a9ac0) {
          *(undefined4 *)((int)this + 0x9d0) = 0;
          CGame__SetCurrentCamera(this,0,*(void **)((int)this + 0x2d4),'\x01');
          CController__RelinquishControl(*(void **)((int)this + 0x2b4));
          *(uint *)((int)this + 0x2c) = (uint)(*(int *)((int)this + 0x9e0) == 1);
        }
        CDXLandscape__ResetCameraPosition();
      }
      puVar8 = CController__GetToControl(*(void **)((int)this + 0x2b4));
      if (puVar8 == &DAT_0089be50) {
        CController__RelinquishControl(*(void **)((int)this + 0x2b4));
        CController__SetToControl(*(void **)((int)this + 0x2b4),&DAT_00679fa8);
        puVar8 = &DAT_0089be50;
      }
      else {
        puVar8 = CController__GetToControl(*(void **)((int)this + 0x2b4));
        if (puVar8 == &DAT_0089be5c) {
          CController__RelinquishControl(*(void **)((int)this + 0x2b4));
          CController__SetToControl(*(void **)((int)this + 0x2b4),&DAT_00679fa8);
          puVar8 = &DAT_0089be5c;
        }
        else {
          puVar8 = &DAT_00679fa8;
        }
      }
      CController__SetToControl(*(void **)((int)this + 0x2b4),puVar8);
      CUnitAI__Unk_00472a90(0x679fa8);
    }
  }
  return;
}
