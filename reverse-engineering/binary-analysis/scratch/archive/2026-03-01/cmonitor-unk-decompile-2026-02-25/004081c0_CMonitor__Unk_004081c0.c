/* address: 0x004081c0 */
/* name: CMonitor__Unk_004081c0 */
/* signature: void __fastcall CMonitor__Unk_004081c0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__Unk_004081c0(void *param_1)

{
  float *pfVar1;
  float fVar2;
  bool bVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  void *pvVar9;
  int iVar10;
  undefined4 *puVar11;
  int iVar12;
  float *pfVar13;
  int *piVar14;
  undefined4 *puVar15;
  int iVar16;
  void *unaff_EDI;
  float *pfVar17;
  float10 fVar18;
  int in_stack_fffffd54;
  float fStack_248;
  void *local_244;
  undefined1 *local_240;
  void *local_23c;
  float fStack_238;
  undefined4 uStack_234;
  float local_230;
  float local_22c;
  float local_228;
  undefined4 local_224;
  float fStack_220;
  float fStack_21c;
  float fStack_218;
  float fStack_210;
  float fStack_20c;
  float fStack_208;
  float fStack_200;
  float fStack_1fc;
  float fStack_1f8;
  float fStack_1f0;
  float fStack_1ec;
  float fStack_1e8;
  undefined4 uStack_1e4;
  float afStack_1e0 [4];
  float fStack_1d0;
  float fStack_1cc;
  float fStack_1c8;
  float fStack_1c0;
  float fStack_1bc;
  float fStack_1b8;
  int iStack_1b0;
  undefined4 uStack_1ac;
  undefined4 uStack_1a8;
  float fStack_1a4;
  float fStack_1a0;
  float fStack_19c;
  float fStack_198;
  float fStack_190;
  float fStack_18c;
  float fStack_188;
  undefined **ppuStack_180;
  undefined4 uStack_17c;
  undefined4 uStack_178;
  undefined4 uStack_174;
  float fStack_16c;
  undefined4 uStack_168;
  undefined4 uStack_164;
  undefined4 uStack_160;
  float fStack_15c;
  undefined4 uStack_158;
  float fStack_154;
  undefined4 uStack_150;
  float fStack_14c;
  float fStack_148;
  float fStack_144;
  float afStack_13c [4];
  float fStack_12c;
  float fStack_128;
  float fStack_124;
  float fStack_11c;
  float fStack_118;
  float fStack_114;
  char acStack_10c [256];
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d122b;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  local_23c = (void *)((int)param_1 + 0x250);
  pvVar9 = (void *)LinkedPtrCursor__MoveFirstAndGet(&local_240);
  while (pvVar9 != (void *)0x0) {
    if (*(float *)((int)pvVar9 + 4) + _DAT_005d8ba0 < DAT_00672fd0) {
      CSPtrSet__Remove((void *)((int)param_1 + 0x250),pvVar9);
      OID__FreeObject(pvVar9);
      break;
    }
    pvVar9 = (void *)LinkedPtrCursor__MoveNextAndGet(&local_240);
  }
  CMonitor__Unk_0040ebf0(param_1);
  *(undefined4 *)((int)param_1 + 0x5d4) = 0;
  if (*(float *)((int)param_1 + 0x5dc) - _DAT_005d85d8 <= *(float *)((int)param_1 + 0x5d8)) {
    if (*(float *)((int)param_1 + 0x5d8) <= *(float *)((int)param_1 + 0x5dc) + _DAT_005d85d8) {
      *(undefined4 *)((int)param_1 + 0x5d8) = *(undefined4 *)((int)param_1 + 0x5dc);
    }
    else {
      *(float *)((int)param_1 + 0x5d8) = *(float *)((int)param_1 + 0x5d8) - _DAT_005d85d8;
    }
  }
  else {
    *(float *)((int)param_1 + 0x5d8) = *(float *)((int)param_1 + 0x5d8) + _DAT_005d85d8;
  }
  if (*(int *)((int)param_1 + 0x314) == 1) {
    if (*(int *)((int)param_1 + 0x4a8) < 1) {
      iVar10 = 0x13;
      puVar11 = (undefined4 *)((int)param_1 + 0x4a4);
      puVar15 = (undefined4 *)((int)param_1 + 0x448);
      do {
        iVar10 = iVar10 + -1;
        *puVar15 = puVar15[-4];
        puVar15[1] = puVar15[-3];
        puVar15[2] = puVar15[-2];
        puVar15[3] = puVar15[-1];
        *puVar11 = puVar11[-1];
        puVar11 = puVar11 + -1;
        puVar15 = puVar15 + -4;
      } while (iVar10 != 0);
      *(undefined4 *)((int)param_1 + 0x318) = *(undefined4 *)((int)param_1 + 0x1c);
      *(undefined4 *)((int)param_1 + 0x31c) = *(undefined4 *)((int)param_1 + 0x20);
      *(undefined4 *)((int)param_1 + 800) = *(undefined4 *)((int)param_1 + 0x24);
      *(undefined4 *)((int)param_1 + 0x324) = *(undefined4 *)((int)param_1 + 0x28);
      *(float *)((int)param_1 + 0x458) = DAT_00672fd0;
    }
    else {
      iVar10 = *(int *)((int)param_1 + 0x4a8) + -1;
      *(int *)((int)param_1 + 0x4a8) = iVar10;
      puVar11 = (undefined4 *)(iVar10 * 0x10 + 0x318 + (int)param_1);
      *puVar11 = *(undefined4 *)((int)param_1 + 0x1c);
      puVar11[1] = *(undefined4 *)((int)param_1 + 0x20);
      puVar11[2] = *(undefined4 *)((int)param_1 + 0x24);
      puVar11[3] = *(undefined4 *)((int)param_1 + 0x28);
      *(float *)((int)param_1 + *(int *)((int)param_1 + 0x4a8) * 4 + 0x458) = DAT_00672fd0;
    }
  }
  *(undefined4 *)((int)param_1 + 0x314) = 1;
  *(float *)((int)param_1 + 0x604) = *(float *)((int)param_1 + 0x604) * _DAT_005d8bec;
  if ((((*(int *)((int)param_1 + 0x574) != 0) && (DAT_008a9ac4 == 0)) &&
      ((*(byte *)((int)param_1 + 0x2c) & 4) == 0)) &&
     (pvVar9 = CGame__GetController
                         (&DAT_008a9a98,*(int *)(*(int *)((int)param_1 + 0x574) + 0x2c) + -1),
     pvVar9 != (void *)0x0)) {
    local_244 = *(void **)((int)param_1 + 0x604);
    if (_DAT_005d856c <= (float)local_244) {
      if (_DAT_005d8568 < (float)local_244) {
        local_244 = (void *)0x3f800000;
      }
    }
    else {
      local_244 = (void *)0x0;
    }
    CUnitAI__Unk_0042e750
              (pvVar9,local_244,(float)(*(int *)(*(int *)((int)param_1 + 0x574) + 0x2c) + -1),
               (int)unaff_EDI);
  }
  if ((*(byte *)((int)param_1 + 0x2c) & 4) == 0) {
    if ((2 < DAT_008a9ac0) && (*(int *)((int)param_1 + 0x70) != 0)) {
      *(undefined4 *)(*(int *)((int)param_1 + 0x70) + 0x2c) = 0;
    }
    if (*(int *)((int)param_1 + 0x2fc) == 0) {
      if (_DAT_005d85cc <= *(float *)((int)param_1 + 0x2f8)) {
        CMonitor__Unk_0040de40(param_1);
      }
    }
    else {
      fVar2 = *(float *)((int)param_1 + 0x2f8) - _DAT_005d8574;
      *(float *)((int)param_1 + 0x2f8) = fVar2;
      if (fVar2 <= _DAT_005d856c) {
        iVar10 = *(int *)(*(int *)((int)param_1 + 0x578) + 0x1c);
        iVar16 = (**(code **)(*(int *)param_1 + 0x1d4))();
        if (iVar10 == iVar16) {
          iVar10 = (**(code **)(*(int *)param_1 + 0x1d4))();
          iVar10 = *(int *)(*(int *)(iVar10 + 0xa4) + 0x34);
          *(undefined4 *)((int)param_1 + 0x588) = 0;
          if (*(int *)((int)param_1 + 0x260) == 2) {
            CMonitor__Unk_00414010();
          }
          else if (*(int *)((int)param_1 + 0x260) == 3) {
            CMonitor__Unk_00412000(*(void **)((int)param_1 + 0x57c));
          }
          iVar16 = (**(code **)(*(int *)param_1 + 0x1d4))();
          if (iVar10 != *(int *)(*(int *)(iVar16 + 0xa4) + 0x34)) {
            *(undefined4 *)((int)param_1 + 0x2cc) = 0x3f800000;
          }
        }
        *(undefined4 *)((int)param_1 + 0x2f8) = 0;
        *(undefined4 *)((int)param_1 + 0x2fc) = 0;
      }
    }
    if ((*(int *)((int)param_1 + 0x4ac) != 0) &&
       (fVar2 = *(float *)((int)param_1 + 0xfc) - *(float *)(*(int *)((int)param_1 + 0x4b0) + 8),
       *(float *)((int)param_1 + 0xfc) = fVar2, fVar2 < _DAT_005d856c)) {
      *(undefined4 *)((int)param_1 + 0xfc) = 0;
      *(undefined4 *)((int)param_1 + 0x5dc) = 0;
      *(undefined4 *)((int)param_1 + 0x4ac) = 0;
    }
    local_244 = (void *)(*(float *)(*(int *)((int)param_1 + 0x4b0) + 0x1c) * _DAT_005d858c);
    fStack_248 = *(float *)(*(int *)((int)param_1 + 0x4b0) + 0x20) * _DAT_005d858c;
    if (((float)local_244 < *(float *)((int)param_1 + 0x2d8)) &&
       (*(float *)((int)param_1 + 0xf8) <= (float)local_244)) {
      *(float *)((int)param_1 + 0x2e0) = DAT_00672fd0;
      sprintf(acStack_10c,s_hud__s_00623314);
      pvVar9 = (void *)CSoundManager__Unk_004e1910(&DAT_00896988,(int)acStack_10c,0,(int)unaff_EDI);
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar9,param_1);
    }
    if ((fStack_248 < *(float *)((int)param_1 + 0x2dc)) &&
       (*(float *)((int)param_1 + 0xfc) <= fStack_248)) {
      *(float *)((int)param_1 + 0x2e4) = DAT_00672fd0;
      sprintf(acStack_10c,s_hud__s_00623314);
      pvVar9 = (void *)CSoundManager__Unk_004e1910(&DAT_00896988,(int)acStack_10c,0,(int)unaff_EDI);
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar9,param_1);
    }
    if (((*(float *)((int)param_1 + 0xf8) <= (float)local_244) &&
        (*(float *)((int)param_1 + 0xf8) <= *(float *)((int)param_1 + 0x2d8))) &&
       (_DAT_005d85d4 < DAT_00672fd0 - *(float *)((int)param_1 + 0x2e0))) {
      *(float *)((int)param_1 + 0x2e0) = DAT_00672fd0;
      sprintf(acStack_10c,s_hud__s_00623314);
      pvVar9 = (void *)CSoundManager__Unk_004e1910(&DAT_00896988,(int)acStack_10c,0,(int)unaff_EDI);
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar9,param_1);
    }
    if (((*(float *)((int)param_1 + 0xfc) <= fStack_248) &&
        (*(float *)((int)param_1 + 0xfc) <= *(float *)((int)param_1 + 0x2dc))) &&
       (_DAT_005d85d4 < DAT_00672fd0 - *(float *)((int)param_1 + 0x2e4))) {
      *(float *)((int)param_1 + 0x2e4) = DAT_00672fd0;
      sprintf(acStack_10c,s_hud__s_00623314);
      pvVar9 = (void *)CSoundManager__Unk_004e1910(&DAT_00896988,(int)acStack_10c,0,(int)unaff_EDI);
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar9,param_1);
    }
    if ((DAT_00672fd0 < *(float *)((int)param_1 + 0x2e8) + _DAT_005d8c44) &&
       (*(float *)((int)param_1 + 0x514) + _DAT_005d8c44 < DAT_00672fd0)) {
      sprintf(acStack_10c,s_hud__s_00623314);
      pvVar9 = (void *)CSoundManager__Unk_004e1910(&DAT_00896988,(int)acStack_10c,0,(int)unaff_EDI);
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar9,param_1);
      *(float *)((int)param_1 + 0x514) = DAT_00672fd0;
    }
    if ((DAT_00672fd0 < *(float *)((int)param_1 + 0x608) + _DAT_005d8c44) &&
       (*(float *)((int)param_1 + 0x518) + _DAT_005d8c44 < DAT_00672fd0)) {
      sprintf(acStack_10c,s_hud__s_00623314);
      pvVar9 = (void *)CSoundManager__Unk_004e1910(&DAT_00896988,(int)acStack_10c,0,(int)unaff_EDI);
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar9,param_1);
      *(float *)((int)param_1 + 0x518) = DAT_00672fd0;
    }
    if ((DAT_00672fd0 < *(float *)((int)param_1 + 0x60c) + _DAT_005d8c44) &&
       (*(float *)((int)param_1 + 0x51c) + _DAT_005d8c44 < DAT_00672fd0)) {
      sprintf(acStack_10c,s_hud__s_00623314);
      pvVar9 = (void *)CSoundManager__Unk_004e1910(&DAT_00896988,(int)acStack_10c,0,(int)unaff_EDI);
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar9,param_1);
      *(float *)((int)param_1 + 0x51c) = DAT_00672fd0;
    }
    *(undefined4 *)((int)param_1 + 0x2d8) = *(undefined4 *)((int)param_1 + 0xf8);
    *(undefined4 *)((int)param_1 + 0x2d0) = *(undefined4 *)((int)param_1 + 0x2c8);
    *(undefined4 *)((int)param_1 + 0x2dc) = *(undefined4 *)((int)param_1 + 0xfc);
    iVar10 = (**(code **)(*(int *)param_1 + 0x1d4))();
    if (iVar10 != 0) {
      iVar16 = *(int *)(*(int *)(iVar10 + 0xa4) + 0x34);
      if (iVar16 == 1) {
        if ((*(float *)((int)param_1 + 0x2cc) < _DAT_005d8c40) &&
           (fVar2 = *(float *)((int)param_1 + 0x2cc) + _DAT_005d85c0,
           *(float *)((int)param_1 + 0x2cc) = fVar2, _DAT_005d8568 < fVar2)) {
LAB_00408b0d:
          *(undefined4 *)((int)param_1 + 0x2cc) = 0x3f800000;
        }
      }
      else if (iVar16 == 2) {
        iVar16 = 0;
        iVar12 = 0;
        piVar14 = (int *)(*(int *)(iVar10 + 0xa4) + 0xc);
        do {
          if (*piVar14 != -1) {
            iVar16 = iVar12;
          }
          iVar12 = iVar12 + 100;
          piVar14 = piVar14 + 1;
        } while (iVar12 < 500);
        fVar2 = _DAT_005d856c;
        if (iVar16 != 0) {
          iVar16 = CMonitor__Unk_00409880(iVar10);
          fVar2 = *(float *)(iVar10 + 0x60) / (float)iVar16;
        }
        fStack_248 = (_DAT_005d8568 - fVar2) * _DAT_005d85f8 + _DAT_005d8604;
        if (_DAT_005d8568 <= fVar2) {
          *(float *)((int)param_1 + 0x2ec) = DAT_00672fd0 + _DAT_005d85ec;
        }
        if (*(float *)((int)param_1 + 0x2cc) <= fStack_248) {
          if ((*(float *)((int)param_1 + 0x2cc) < fStack_248) &&
             (*(float *)((int)param_1 + 0x2ec) < DAT_00672fd0)) goto LAB_00408b0d;
        }
        else {
          *(float *)((int)param_1 + 0x2cc) = fStack_248;
        }
      }
    }
    if ((float)_DAT_005d8c38 <=
        ABS(*(float *)((int)param_1 + 0x2cc) - *(float *)((int)param_1 + 0x2c8))) {
      if (*(float *)((int)param_1 + 0x2cc) <= *(float *)((int)param_1 + 0x2c8)) {
        if (*(float *)((int)param_1 + 0x2c8) <= *(float *)((int)param_1 + 0x2cc)) goto LAB_00408b82;
        fVar2 = *(float *)((int)param_1 + 0x2c8) - _DAT_005d85c0;
      }
      else {
        fVar2 = *(float *)((int)param_1 + 0x2c8) + _DAT_005d85c0;
      }
      *(float *)((int)param_1 + 0x2c8) = fVar2;
    }
    else {
      *(undefined4 *)((int)param_1 + 0x2c8) = *(undefined4 *)((int)param_1 + 0x2cc);
    }
LAB_00408b82:
    CBattleEngine__Unk_00406560((int)param_1);
    if (*(int *)((int)param_1 + 0x260) == 3) {
      *(uint *)((int)param_1 + 0x34) = *(uint *)((int)param_1 + 0x34) & 0xfffdfdff | 0x400;
    }
    else {
      *(uint *)((int)param_1 + 0x34) = *(uint *)((int)param_1 + 0x34) & 0xfffffbff | 0x20200;
    }
    iVar10 = *(int *)((int)param_1 + 0x574);
    if (*(int *)((int)param_1 + 0x260) == 3) {
      if ((iVar10 != 0) && (*(int *)(iVar10 + 0x28) == 2)) {
        CPlayer__dtor();
      }
      if (*(float *)((int)param_1 + 0xfc) == _DAT_005d856c) {
        if ((*(int *)((int)param_1 + 0x59c) != 0) &&
           (piVar14 = CSoundManager__Unk_004e1880
                                (&DAT_00896988,*(int *)((int)param_1 + 0x59c) + 0x40,param_1,
                                 (int)unaff_EDI), piVar14 != (int *)0x0)) {
          CSoundManager__Unk_004e1260(&DAT_00896988,piVar14[3],0,0.02,(float)param_1,(int)unaff_EDI)
          ;
        }
      }
      else {
        iVar10 = CSoundManager__Unk_004e1ab0
                           (&DAT_00896988,*(int *)((int)param_1 + 0x59c),(int)param_1,(int)unaff_EDI
                           );
        if (iVar10 == 0) {
          CSoundManager__Unk_004e1940(&DAT_00896988,*(void **)((int)param_1 + 0x59c),param_1);
        }
        piVar14 = CSoundManager__Unk_004e1880
                            (&DAT_00896988,*(int *)((int)param_1 + 0x59c) + 0x40,param_1,
                             (int)unaff_EDI);
        CSoundManager__Unk_004e18d0
                  (&DAT_00896988,(int)piVar14,
                   (int)(*(float *)(*(int *)((int)param_1 + 0x57c) + 0x20) * _DAT_005d858c +
                        _DAT_005d8568),0,(float)unaff_EDI);
      }
      OID_Unk_005078f0__Wrapper_00410c50(*(void **)((int)param_1 + 0x57c));
      if (*(int *)((int)param_1 + 0x580) == 0) {
        CGeneralVolume__Unk_0040a580(param_1);
      }
    }
    else {
      if ((iVar10 != 0) && (*(int *)(iVar10 + 0x28) == 2)) {
        CPlayer__Unk_004d2a50(iVar10);
      }
      if (*(int *)((int)param_1 + 0x260) == 1) {
        if (_DAT_005d8c30 < *(float *)((int)param_1 + 0x118)) {
          *(float *)((int)param_1 + 0x280) = *(float *)((int)param_1 + 0x280) - _DAT_005d8c2c;
        }
        if ((*(float *)((int)param_1 + 0x2f0) - _DAT_005d85c0 < *(float *)((int)param_1 + 0x24)) &&
           (DAT_00672fd0 < *(float *)((int)param_1 + 0x2f4) + _DAT_005d8ba0)) {
          *(float *)((int)param_1 + 0x84) = *(float *)((int)param_1 + 0x84) - _DAT_005d8bec;
          CMonitor__Unk_00413760(*(void **)((int)param_1 + 0x578));
          goto LAB_00408d75;
        }
        fStack_248 = DAT_00672fd0 + _DAT_005d85ec;
        CEventManager__AddEvent_AtTime
                  (&EVENT_MANAGER,6000,param_1,&fStack_248,0,(void *)0x0,(void *)0x0);
      }
      CMonitor__Unk_00413760(*(void **)((int)param_1 + 0x578));
    }
  }
  else {
    if (*(void **)((int)param_1 + 0x5fc) != (void *)0x0) {
      CMonitor__Unk_004097a0
                (*(void **)((int)param_1 + 0x5fc),(void *)((int)param_1 + 0x1c),unaff_EDI);
    }
    if (*(int *)((int)param_1 + 0x260) == 3) {
      *(undefined4 *)((int)param_1 + 0x280) = 0x3c23d70a;
      local_244 = (void *)SQRT(*(float *)((int)param_1 + 0x84) * *(float *)((int)param_1 + 0x84) +
                               *(float *)((int)param_1 + 0x80) * *(float *)((int)param_1 + 0x80) +
                               *(float *)((int)param_1 + 0x7c) * *(float *)((int)param_1 + 0x7c));
      local_228 = (float)local_244 * *(float *)((int)param_1 + 0x60);
      local_22c = (float)local_244 * *(float *)((int)param_1 + 0x50);
      local_230 = (float)local_244 * *(float *)((int)param_1 + 0x40);
      *(float *)((int)param_1 + 0x7c) = local_230;
      *(float *)((int)param_1 + 0x80) = local_22c;
      *(float *)((int)param_1 + 0x84) = local_228;
      *(undefined4 *)((int)param_1 + 0x88) = local_224;
    }
  }
LAB_00408d75:
  if (_DAT_005d8570 <=
      SQRT(*(float *)((int)param_1 + 0x84) * *(float *)((int)param_1 + 0x84) +
           *(float *)((int)param_1 + 0x80) * *(float *)((int)param_1 + 0x80) +
           *(float *)((int)param_1 + 0x7c) * *(float *)((int)param_1 + 0x7c))) {
    *(undefined4 *)((int)param_1 + 0x310) = 0;
  }
  else {
    iVar10 = *(int *)((int)param_1 + 0x310) + 1;
    *(int *)((int)param_1 + 0x310) = iVar10;
    if (5 < iVar10) {
      (**(code **)(*(int *)param_1 + 0x110))();
    }
  }
  fVar18 = (float10)(**(code **)(*(int *)param_1 + 0xb4))();
  pfVar1 = (float *)((int)param_1 + 0x1c);
  fStack_248 = (float)(fVar18 + (float10)*(float *)((int)param_1 + 0x84));
  bVar3 = _DAT_005d856c <= *pfVar1;
  *(float *)((int)param_1 + 0x84) = fStack_248;
  if (bVar3) {
    if ((_DAT_005d8c28 < *pfVar1) && (_DAT_005d856c < *(float *)((int)param_1 + 0x7c))) {
      fVar2 = _DAT_005d8568 - (*pfVar1 - _DAT_005d8c28) * _DAT_005d8584;
      goto joined_r0x00408e6c;
    }
  }
  else if (*(float *)((int)param_1 + 0x7c) < _DAT_005d856c) {
    fVar2 = (*pfVar1 + _DAT_005d857c) * _DAT_005d8584;
joined_r0x00408e6c:
    if (fVar2 < _DAT_005d856c) {
      fVar2 = _DAT_005d856c;
    }
    *(float *)((int)param_1 + 0x7c) = fVar2 * *(float *)((int)param_1 + 0x7c);
  }
  if (_DAT_005d856c <= *(float *)((int)param_1 + 0x20)) {
    if ((*(float *)((int)param_1 + 0x20) <= _DAT_005d8c28) ||
       (*(float *)((int)param_1 + 0x80) <= _DAT_005d856c)) goto LAB_00408f16;
    fVar2 = _DAT_005d8568 - (*(float *)((int)param_1 + 0x20) - _DAT_005d8c28) * _DAT_005d8584;
  }
  else {
    if (_DAT_005d856c <= *(float *)((int)param_1 + 0x80)) goto LAB_00408f16;
    fVar2 = (*(float *)((int)param_1 + 0x20) + _DAT_005d857c) * _DAT_005d8584;
  }
  if (fVar2 < _DAT_005d856c) {
    fVar2 = _DAT_005d856c;
  }
  *(float *)((int)param_1 + 0x80) = fVar2 * *(float *)((int)param_1 + 0x80);
LAB_00408f16:
  if ((*(float *)((int)param_1 + 0x24) < _DAT_005d8c24) && (fStack_248 < _DAT_005d856c)) {
    fVar2 = (*(float *)((int)param_1 + 0x24) + _DAT_005d8c20) * _DAT_005d8c1c;
    if (fVar2 < _DAT_005d856c) {
      fVar2 = _DAT_005d856c;
    }
    *(float *)((int)param_1 + 0x84) = fStack_248 * fVar2;
  }
  CUnit__Unk_004015e0(param_1);
  fStack_1f0 = *pfVar1;
  fStack_1ec = *(float *)((int)param_1 + 0x20);
  fStack_1e8 = *(float *)((int)param_1 + 0x24);
  uStack_1e4 = *(undefined4 *)((int)param_1 + 0x28);
  iVar10 = HeightDelta__Below015_D4((int)param_1);
  if (((iVar10 == 0) || (*(int **)((int)param_1 + 0x264) == (int *)0x0)) ||
     (pfVar13 = (float *)(**(code **)(**(int **)((int)param_1 + 0x264) + 0x6c))(),
     pfVar13[2] * pfVar13[2] + pfVar13[1] * pfVar13[1] + *pfVar13 * *pfVar13 <= _DAT_005d856c)) {
    local_230 = 0.0;
    local_22c = 0.0;
    local_228 = 0.0;
    *(undefined4 *)((int)param_1 + 0x268) = 0;
    *(undefined4 *)((int)param_1 + 0x26c) = 0;
    *(undefined4 *)((int)param_1 + 0x270) = 0;
    *(undefined4 *)((int)param_1 + 0x274) = local_224;
  }
  else {
    pfVar13 = (float *)(**(code **)(**(int **)((int)param_1 + 0x264) + 0x6c))();
    *(float *)((int)param_1 + 0x268) = *pfVar13;
    *(float *)((int)param_1 + 0x26c) = pfVar13[1];
    *(float *)((int)param_1 + 0x270) = pfVar13[2];
    *(float *)((int)param_1 + 0x274) = pfVar13[3];
    *pfVar1 = *pfVar1 + *(float *)((int)param_1 + 0x268);
    *(float *)((int)param_1 + 0x20) =
         *(float *)((int)param_1 + 0x26c) + *(float *)((int)param_1 + 0x20);
    *(float *)((int)param_1 + 0x24) =
         *(float *)((int)param_1 + 0x270) + *(float *)((int)param_1 + 0x24);
    (**(code **)(**(int **)((int)param_1 + 0x264) + 0x7c))();
    fVar8 = fStack_1fc;
    fVar7 = fStack_200;
    fVar6 = fStack_208;
    fVar5 = fStack_210;
    fVar4 = fStack_218;
    fVar2 = fStack_21c;
    pfVar13 = (float *)(*(int *)((int)param_1 + 0x264) + 0x3c);
    if ((*(uint *)(*(int *)((int)param_1 + 0x264) + 0x34) & 0x80000000) == 0) {
      pfVar13 = (float *)&DAT_0083d9c0;
    }
    pfVar17 = afStack_1e0;
    for (iVar10 = 0xc; iVar10 != 0; iVar10 = iVar10 + -1) {
      *pfVar17 = *pfVar13;
      pfVar13 = pfVar13 + 1;
      pfVar17 = pfVar17 + 1;
    }
    if (((((fStack_220 != afStack_1e0[0]) || (fStack_21c != afStack_1e0[1])) ||
         ((fStack_218 != afStack_1e0[2] ||
          ((fStack_210 != fStack_1d0 || (fStack_20c != fStack_1cc)))))) ||
        (fStack_208 != fStack_1c8)) ||
       (((fStack_200 != fStack_1c0 || (fStack_1fc != fStack_1bc)) || (fStack_1f8 != fStack_1b8)))) {
      fStack_210 = fStack_21c;
      fStack_218 = fStack_200;
      fStack_200 = fVar4;
      fStack_208 = fStack_1fc;
      fStack_21c = fVar5;
      fStack_1fc = fVar6;
      fStack_238 = fStack_1c0 * fVar7 + fStack_1bc * fVar8 + fStack_1b8 * fStack_1f8;
      local_23c = (void *)(fStack_1b8 * fVar6 + fStack_1c0 * fVar5 + fStack_1bc * fStack_20c);
      local_240 = (undefined1 *)(fStack_1c0 * fStack_220 + fStack_1bc * fVar2 + fStack_1b8 * fVar4);
      fStack_190 = fStack_1d0 * fStack_220 + fStack_1cc * fVar2 + fStack_1c8 * fVar4;
      fStack_18c = fStack_1c8 * fVar6 + fStack_1d0 * fVar5 + fStack_1cc * fStack_20c;
      fStack_188 = fStack_1d0 * fVar7 + fStack_1cc * fVar8 + fStack_1c8 * fStack_1f8;
      fStack_1a0 = afStack_1e0[0] * fStack_220 + fVar2 * afStack_1e0[1] + fVar4 * afStack_1e0[2];
      fStack_248 = afStack_1e0[2] * fVar6 + fVar5 * afStack_1e0[0] + fStack_20c * afStack_1e0[1];
      local_244 = (void *)(fVar7 * afStack_1e0[0] +
                          fVar8 * afStack_1e0[1] + fStack_1f8 * afStack_1e0[2]);
      fStack_19c = fStack_248;
      fStack_198 = (float)local_244;
      Mat34__SetRows();
      iVar10 = *(int *)((int)param_1 + 0x264);
      fVar2 = *(float *)((int)param_1 + 0x24);
      pfVar13 = afStack_13c;
      pfVar17 = afStack_1e0;
      for (iVar16 = 0xc; iVar16 != 0; iVar16 = iVar16 + -1) {
        *pfVar17 = *pfVar13;
        pfVar13 = pfVar13 + 1;
        pfVar17 = pfVar17 + 1;
      }
      fVar2 = fVar2 - *(float *)(iVar10 + 0x24);
      fVar5 = *(float *)((int)param_1 + 0x20) - *(float *)(iVar10 + 0x20);
      fVar4 = *pfVar1 - *(float *)(iVar10 + 0x1c);
      fStack_248 = fStack_114 * fVar2 + fStack_118 * fVar5 + fStack_11c * fVar4;
      local_244 = (void *)(fStack_12c * fVar4 + fStack_124 * fVar2 + fStack_128 * fVar5);
      fStack_238 = fStack_248 + *(float *)(iVar10 + 0x24);
      local_23c = (void *)((float)local_244 + *(float *)(iVar10 + 0x20));
      local_240 = (undefined1 *)
                  (afStack_13c[2] * fVar2 + afStack_13c[1] * fVar5 + afStack_13c[0] * fVar4 +
                  *(float *)(iVar10 + 0x1c));
      *pfVar1 = (float)local_240;
      *(void **)((int)param_1 + 0x20) = local_23c;
      *(float *)((int)param_1 + 0x24) = fStack_238;
      *(undefined4 *)((int)param_1 + 0x28) = uStack_234;
      CExplosionInitThing__Unk_0044adb0(&local_230,afStack_1e0,(int)unaff_EDI);
      *(float *)((int)param_1 + 0x114) = local_230 + *(float *)((int)param_1 + 0x114);
    }
  }
  fStack_144 = *(float *)((int)param_1 + 0x24) - fStack_1e8;
  fStack_148 = *(float *)((int)param_1 + 0x20) - fStack_1ec;
  fStack_14c = *pfVar1 - fStack_1f0;
  if (*(int *)((int)param_1 + 0x70) != 0) {
    CMCMech__TranslatePositions();
  }
  fStack_1f0 = *pfVar1;
  fStack_16c = *pfVar1;
  fStack_1e8 = *(float *)((int)param_1 + 0x24) + _DAT_005d8c18;
  uStack_168 = *(undefined4 *)((int)param_1 + 0x20);
  fStack_1ec = *(float *)((int)param_1 + 0x20);
  uStack_164 = *(undefined4 *)((int)param_1 + 0x24);
  uStack_160 = *(undefined4 *)((int)param_1 + 0x28);
  uStack_17c = 0;
  uStack_178 = 0;
  uStack_174 = 0;
  uStack_150 = uStack_1e4;
  ppuStack_180 = &PTR_VFuncSlot_00_00426340_005d8bfc;
  local_240 = &stack0xfffffd54;
  uStack_4 = 0;
  iStack_1b0 = 0;
  uStack_1ac = 0xffffffff;
  uStack_1a8 = 0;
  fStack_1a4 = -1.0;
  fStack_15c = fStack_1f0;
  uStack_158 = fStack_1ec;
  fStack_154 = fStack_1e8;
  CGeneralVolume__ctor_like_004098e0(&stack0xfffffd54,&ppuStack_180,in_stack_fffffd54);
  CWorld__Unk_0050b030();
  fStack_248 = fStack_1a4;
  if (((_DAT_005d856c < fStack_1a4) &&
      (fVar18 = (float10)(**(code **)(*(int *)param_1 + 0xc0))(), (float10)fStack_248 < fVar18)) &&
     ((iStack_1b0 != 0 && ((*(uint *)(iStack_1b0 + 0x34) & 0x100000) != 0)))) {
    fVar18 = (float10)(**(code **)(*(int *)param_1 + 0xc0))();
    *(float *)((int)param_1 + 0x24) =
         (float)(((float10)fStack_248 - fVar18) + (float10)*(float *)((int)param_1 + 0x24));
    (**(code **)(*(int *)param_1 + 0x118))();
    (**(code **)(*(int *)param_1 + 0x110))();
  }
  CMonitor__Unk_00407a50(param_1);
  pfVar13 = (float *)((int)param_1 + 0x52c);
  iVar10 = 6;
  do {
    if (pfVar13[0xc] != 0.0) {
      fStack_248 = *pfVar13 - (float)_DAT_00622f08;
      *pfVar13 = fStack_248;
      if (_DAT_005d856c <= fStack_248) {
        if (fStack_248 <
            *(float *)(*(int *)((int)param_1 + 0x4b0) + (-0x4a4 - (int)param_1) + (int)pfVar13) *
            _DAT_005d8bc4) {
          pfVar13[6] = 0.0;
        }
      }
      else {
        *pfVar13 = 0.0;
      }
    }
    pfVar13 = pfVar13 + 1;
    iVar10 = iVar10 + -1;
  } while (iVar10 != 0);
  CGeneralVolume__Unk_0040b120(param_1);
  CGeneralVolume__Unk_00409950(param_1);
  if (*(int *)((int)param_1 + 0x638) == 0) {
    CMonitor__Unk_0040eb50((int)param_1);
  }
  else {
    iVar10 = CMapWho__GetFirstEntryWithinRadius();
    while (iVar10 != 0) {
      piVar14 = (int *)CMapWhoEntry__GetOwner();
      if (((piVar14 != (int *)0x0) && ((*(byte *)(piVar14 + 0xd) & 0x10) != 0)) &&
         ((piVar14 != param_1 &&
          ((*(float *)((int)param_1 + 0x24) - _DAT_005d8ba0 < (float)piVar14[9] &&
           (fVar2 = (float)piVar14[8] - *(float *)((int)param_1 + 0x20),
           fStack_248 = (float)piVar14[9] - *(float *)((int)param_1 + 0x24),
           SQRT(fStack_248 * fStack_248 +
                fVar2 * fVar2 + ((float)piVar14[7] - *pfVar1) * ((float)piVar14[7] - *pfVar1)) <
           _DAT_005d8bf4)))))) {
        (**(code **)(*piVar14 + 0xa0))();
      }
      iVar10 = CMapWho__GetNextEntryWithinRadius();
    }
    CGeneralVolume__Unk_0040ef20((int)param_1);
    CMonitor__Unk_0040e940(param_1);
  }
  *(undefined4 *)((int)param_1 + 0x638) = 0;
  ExceptionList = pvStack_c;
  return;
}
