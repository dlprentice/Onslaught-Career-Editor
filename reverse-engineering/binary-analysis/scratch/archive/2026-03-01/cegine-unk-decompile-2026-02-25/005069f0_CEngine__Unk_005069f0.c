/* address: 0x005069f0 */
/* name: CEngine__Unk_005069f0 */
/* signature: int __fastcall CEngine__Unk_005069f0(void * param_1) */


/* WARNING: Type propagation algorithm not settling */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CEngine__Unk_005069f0(void *param_1)

{
  float fVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  float *pfVar5;
  undefined4 uVar6;
  int *piVar7;
  uint uVar8;
  uint uVar9;
  float *extraout_EAX;
  int iVar10;
  int *piVar11;
  int unaff_EBP;
  int *unaff_ESI;
  int iVar12;
  void *pvVar13;
  void *unaff_EDI;
  int *piVar14;
  undefined ***pppuVar15;
  undefined4 *puVar16;
  float10 extraout_ST0;
  float10 fVar17;
  double dVar18;
  void *pvVar19;
  undefined1 *puVar20;
  float fVar21;
  int *piVar22;
  int *local_a84;
  float local_a80;
  float fStack_a7c;
  float fStack_a78;
  float fStack_a74;
  undefined4 local_a68;
  undefined4 uStack_a64;
  float fStack_a60;
  undefined4 uStack_a5c;
  int local_a58;
  undefined1 auStack_a54 [4];
  void *pvStack_a50;
  int local_a4c;
  undefined4 auStack_a28 [5];
  undefined1 local_a14 [76];
  undefined1 auStack_9c8 [48];
  undefined4 *puStack_998;
  int *piStack_994;
  void *pvStack_990;
  float fStack_98c;
  float fStack_97c;
  float fStack_978;
  float fStack_974;
  float fStack_970;
  float fStack_96c;
  undefined4 uStack_968;
  undefined4 uStack_964;
  undefined4 uStack_960;
  float fStack_95c;
  float fStack_94c;
  float fStack_948;
  float local_944;
  undefined4 local_940;
  undefined4 local_93c;
  float local_938;
  float fStack_934;
  float fStack_930;
  float fStack_924;
  undefined4 uStack_91c;
  undefined4 uStack_918;
  undefined4 uStack_914;
  undefined4 uStack_910;
  float fStack_908;
  float fStack_904;
  float fStack_900;
  float afStack_8ec [13];
  undefined1 auStack_8b8 [112];
  undefined4 auStack_848 [12];
  int aiStack_818 [11];
  undefined1 auStack_7ec [4];
  float fStack_7e8;
  float fStack_7e4;
  float fStack_7e0;
  undefined4 uStack_7dc;
  undefined **appuStack_7d8 [6];
  undefined4 auStack_7c0 [9];
  undefined4 uStack_79c;
  undefined4 uStack_798;
  undefined4 uStack_794;
  undefined4 uStack_790;
  undefined4 uStack_78c;
  int iStack_74c;
  undefined4 uStack_430;
  undefined4 uStack_42c;
  undefined4 uStack_428;
  undefined4 uStack_424;
  int iStack_41c;
  undefined4 local_418;
  float local_414;
  undefined4 local_410;
  float local_40c;
  undefined4 local_408;
  undefined4 local_404;
  undefined4 local_400;
  undefined4 local_3fc [13];
  undefined1 auStack_3c8 [4];
  undefined4 uStack_3c4;
  undefined4 uStack_3c0;
  float fStack_3bc;
  undefined4 uStack_3b8;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d591b;
  local_c = ExceptionList;
  iVar12 = 0;
  ExceptionList = &local_c;
  if (((*(byte *)((int)*(void **)((int)param_1 + 8) + 0x34) & 8) != 0) &&
     (ExceptionList = &local_c,
     iVar2 = CGeneralVolume__Unk_0040c2e0(*(void **)((int)param_1 + 8),(int)param_1,(int)unaff_EDI),
     iVar2 == 0)) {
    ExceptionList = local_c;
    return 0;
  }
  piVar11 = *(int **)((int)param_1 + 0xa0);
  if (piVar11 != (int *)0x0) {
    local_a84 = piVar11;
    if ((piVar11[3] != 0) && (piVar11[0x2d] == 0)) {
      pvVar19 = *(void **)((int)param_1 + 8);
      if ((*(byte *)((int)pvVar19 + 0x34) & 8) == 0) {
        pvVar13 = (void *)piVar11[3];
      }
      else {
        pvVar13 = (void *)piVar11[3];
        pvVar19 = (void *)0x0;
      }
      CSoundManager__Unk_004e1940(&DAT_00896988,pvVar13,pvVar19);
    }
    local_a4c = 0;
    if (0 < piVar11[0x12]) {
LAB_00506aaa:
      local_a80 = (float)CWorldPhysicsManager__CreateProjectile(piVar11[6]);
      piVar22 = unaff_ESI;
      if (local_a80 != 0.0) {
        CInfluenceMap__Init();
        local_944 = -1.0;
        local_940 = 0xbf800000;
        local_418 = 0xbf800000;
        local_414 = -1.0;
        pvVar19 = *(void **)((int)param_1 + 0xa0);
        local_93c = 0xbf800000;
        iVar12 = *(int *)((int)param_1 + 0x70) + 1;
        local_40c = local_938;
        appuStack_7d8[1] = &PTR_VFuncSlot_00_0040e1b0_005de9b4;
        local_410 = 0xbf800000;
        local_408 = 0;
        local_404 = 0;
        local_400 = 0;
        local_3fc[0] = 0;
        *(int *)((int)param_1 + 0x70) = iVar12;
        if (pvVar19 == (void *)0x0) {
          local_a58 = 1;
        }
        else {
          if (*(int *)((int)pvVar19 + 0x58) <= iVar12) {
            *(undefined4 *)((int)param_1 + 0x70) = 0;
          }
          local_a58 = CEngine__Unk_005078b0(pvVar19,*(int *)((int)param_1 + 0x70),(int)unaff_EDI);
        }
        iVar12 = *(int *)((int)param_1 + 0x74) + 1;
        *(int *)((int)param_1 + 0x74) = iVar12;
        if ((*(int *)((int)param_1 + 0xa0) != 0) &&
           (*(int *)(*(int *)((int)param_1 + 0xa0) + 0x68) <= iVar12)) {
          *(undefined4 *)((int)param_1 + 0x74) = 0;
        }
        pvVar19 = param_1;
        (**(code **)(**(int **)((int)param_1 + 8) + 300))(param_1,local_a58,&local_a68,local_a14,1);
        if (*(int *)((int)param_1 + 0x80) != 0) {
          if ((piVar11[0x2b] != 0) &&
             ((((iVar12 = *(int *)(*(int *)((int)param_1 + 0xa0) + 0x18),
                *(float *)(iVar12 + 0x3c) * _DAT_005d8c6c == _DAT_005d856c ||
                (*(int *)(iVar12 + 0x50) != 0)) || (*(int *)(iVar12 + 0x6c) != 0)) &&
              (*(void **)((int)param_1 + 0x2c) != (void *)0x0)))) {
            CThing__Unk_004f3ac0(*(void **)((int)param_1 + 0x2c),(int)&fStack_908,pvVar19);
            fStack_930 = fStack_900 - fStack_a74;
            fStack_934 = fStack_904 - fStack_a78;
            local_938 = fStack_908 - fStack_a7c;
            dVar18 = SQRT__Wrapper_004026b0(&local_938);
            if ((float)dVar18 <= _DAT_005d856c) {
              local_a80 = 0.0;
            }
            else {
              local_a80 = fStack_930 / (float)dVar18;
              CDXTexture__Unk_0055dcb0();
              local_a80 = (float)extraout_ST0;
            }
            fVar17 = (float10)fpatan((float10)local_938,(float10)fStack_934);
            CBattleEngine__Unk_004062d0
                      (auStack_848,(void *)(float)-fVar17,local_a80,0.0,(float)pvVar19);
            puVar3 = auStack_848;
            puVar16 = (undefined4 *)((int)param_1 + 0x30);
            for (iVar12 = 0xc; iVar12 != 0; iVar12 = iVar12 + -1) {
              *puVar16 = *puVar3;
              puVar3 = puVar3 + 1;
              puVar16 = puVar16 + 1;
            }
          }
          puVar3 = (undefined4 *)((int)param_1 + 0x30);
          puVar16 = auStack_a28;
          for (iVar12 = 0xc; iVar12 != 0; iVar12 = iVar12 + -1) {
            *puVar16 = *puVar3;
            puVar3 = puVar3 + 1;
            puVar16 = puVar16 + 1;
          }
        }
        piStack_994 = piVar11 + 0x17;
        pvVar13 = (void *)0x0;
        puVar3 = (undefined4 *)LinkedPtrCursor__MoveFirstAndGet(&puStack_998);
        while (puVar3 != (undefined4 *)0x0) {
          if (pvVar13 == unaff_EDI) goto LAB_00506d3d;
          puStack_998 = (undefined4 *)puStack_998[1];
          pvVar13 = (void *)((int)pvVar13 + 1);
          if (puStack_998 == (undefined4 *)0x0) {
            puVar3 = (undefined4 *)0x0;
          }
          else {
            puVar3 = (undefined4 *)*puStack_998;
          }
        }
        puVar3 = (undefined4 *)0x0;
LAB_00506d3d:
        CUnit__Unk_004f8140(&local_a58,(void *)0x0,1,0,(int)pvVar19);
        if (puVar3 != (undefined4 *)0x0) {
          fStack_98c = (float)puVar3[1];
          pvStack_990 = (void *)*puVar3;
          CBattleEngine__Unk_004062d0(aiStack_818,pvStack_990,fStack_98c,0.0,(float)pvVar19);
          piVar7 = aiStack_818;
          piVar14 = &local_a58;
          for (iVar12 = 0xc; iVar12 != 0; iVar12 = iVar12 + -1) {
            *piVar14 = *piVar7;
            piVar7 = piVar7 + 1;
            piVar14 = piVar14 + 1;
          }
        }
        if (*(int *)(*(int *)(unaff_EBP + 0xf0) + 0x50) == 0) {
          fStack_924 = *(float *)(*(int *)(unaff_EBP + 0xf0) + 0x2c) * _DAT_005d8584;
        }
        else {
          uStack_968 = 0;
          uStack_964 = 0;
          uStack_960 = 0;
          dVar18 = CEngine__Unk_005099a0(param_1,(void *)0x0,0.0,0.0,fStack_95c);
          fStack_924 = (float)dVar18;
        }
        uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
        uVar4 = uVar4 & 0x8000ffff;
        if ((int)uVar4 < 0) {
          uVar4 = (uVar4 - 1 | 0xffff0000) + 1;
        }
        unaff_EDI = (void *)(((float)(int)uVar4 * _DAT_005d8de4 - _DAT_005d8568) *
                            (float)piVar11[0xd]);
        uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
        uVar4 = uVar4 & 0x8000ffff;
        if ((int)uVar4 < 0) {
          uVar4 = (uVar4 - 1 | 0xffff0000) + 1;
        }
        CBattleEngine__Unk_004062d0
                  (auStack_9c8,
                   (void *)(((float)(int)uVar4 * _DAT_005d8de4 - _DAT_005d8568) *
                           (float)piVar11[0xd]),(float)unaff_EDI,0.0,(float)pvVar19);
        puVar20 = auStack_8b8;
        pfVar5 = (float *)(**(code **)(**(int **)((int)param_1 + 8) + 0x6c))();
        local_944 = fStack_a78 + pfVar5[2];
        fStack_948 = fStack_a7c + pfVar5[1];
        fStack_94c = local_a80 + *pfVar5;
        uStack_7dc = local_940;
        uStack_430 = *(undefined4 *)((int)param_1 + 0x84);
        uStack_42c = *(undefined4 *)((int)param_1 + 0x88);
        uStack_428 = *(undefined4 *)((int)param_1 + 0x8c);
        uStack_424 = *(undefined4 *)((int)param_1 + 0x90);
        fStack_7e8 = fStack_94c;
        fStack_7e4 = fStack_948;
        fStack_7e0 = local_944;
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        Mat34__SetRows();
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        Vec3__SetXYZ();
        Mat34__SetRows();
        pfVar5 = afStack_8ec;
        pppuVar15 = appuStack_7d8;
        for (iVar12 = 0xc; iVar12 != 0; iVar12 = iVar12 + -1) {
          *pppuVar15 = (undefined **)*pfVar5;
          pfVar5 = pfVar5 + 1;
          pppuVar15 = pppuVar15 + 1;
        }
        Vec3__SetXYZ();
        uStack_79c = uStack_91c;
        uStack_794 = uStack_914;
        uStack_798 = uStack_918;
        uStack_790 = uStack_910;
        uStack_78c = 1;
        iStack_74c = (*(int **)((int)param_1 + 8))[0x4e];
        iStack_41c = piVar11[6];
        local_414 = *(float *)(iStack_41c + 0x24);
        pvVar19 = (void *)(**(code **)(**(int **)((int)param_1 + 8) + 0x144))();
        CGenericActiveReader__SetReader(unaff_ESI + 0x3b,*(void **)((int)param_1 + 8));
        if ((*(int *)(unaff_ESI[0x3c] + 0x4c) != 0) && (pvVar19 != (void *)0x0)) {
          Vec3__SetXYZ();
          fStack_a60 = *(float *)(unaff_ESI[0x3c] + 0x2c);
          fVar21 = SQRT(fStack_97c * fStack_97c + fStack_974 * fStack_974 + fStack_978 * fStack_978)
          ;
          if (fVar21 < fStack_a60 * local_414) {
            uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
            uVar4 = uVar4 & 0x8000ffff;
            if ((int)uVar4 < 0) {
              uVar4 = (uVar4 - 1 | 0xffff0000) + 1;
            }
            piVar22 = (int *)(*(float *)(unaff_ESI[0x3c] + 0x7c) * fVar21);
            fVar1 = (float)(int)uVar4 * _DAT_005de9ac * _DAT_005d85fc * (float)piVar22;
            local_414 = (((fVar1 + fVar1) - (float)piVar22) + fVar21) / fStack_a60;
          }
        }
        pvVar13 = *(void **)((int)param_1 + 8);
        if ((*(byte *)((int)pvVar13 + 0x34) & 8) != 0) {
          piVar7 = (int *)(*(int *)((int)pvVar13 + 0x574) + 0x34);
          *piVar7 = *piVar7 + 1;
          iVar12 = CEngine__Unk_00407310(pvVar13,(int)param_1,(int)puVar20);
          if (iVar12 != 0) {
            CMonitor__Unk_00407060(pvVar13,(int)pvVar19,(int)puVar20);
          }
        }
        CEngine__Unk_004daab0(unaff_ESI,pvVar19,(void *)0x0,(int)puVar20);
        (**(code **)(*unaff_ESI + 0x24))(auStack_7ec);
        if (piVar11[1] != 0) {
          iVar12 = 0;
          piVar7 = (int *)((int)param_1 + 0x18);
LAB_005074f7:
          if (*piVar7 != 0) goto code_r0x005074fc;
          iVar2 = *(int *)(*(int *)((int)param_1 + 8) + 0x164);
          if (iVar2 == 0) {
            uVar6 = 1;
          }
          else {
            uVar6 = *(undefined4 *)(iVar2 + 0x1a4);
          }
          iVar2 = (int)param_1 + iVar12 * 8 + 0x14;
          CParticleManager__CreateEffect
                    (piVar11[1],iVar2,DAT_00855040,DAT_00855044,DAT_00855048,DAT_0085504c,0,uVar6);
          if (*(void **)(iVar2 + 4) != (void *)0x0) {
            CMonitor__Unk_004097a0(*(void **)(iVar2 + 4),&local_a68,unaff_EDI);
          }
          iVar2 = *(int *)(iVar2 + 4);
          if (iVar2 != 0) {
            puVar3 = auStack_7c0;
            puVar16 = (undefined4 *)(iVar2 + 0x10);
            for (iVar10 = 0xc; iVar10 != 0; iVar10 = iVar10 + -1) {
              *puVar16 = *puVar3;
              puVar3 = puVar3 + 1;
              puVar16 = puVar16 + 1;
            }
            *(undefined4 *)(iVar2 + 0xa0) = 1;
          }
          *(int *)((int)param_1 + iVar12 * 4 + 0x24) = local_a58;
          goto LAB_00507652;
        }
        goto LAB_00507680;
      }
      goto LAB_0050787d;
    }
  }
  ExceptionList = local_c;
  return iVar12;
code_r0x005074fc:
  iVar12 = iVar12 + 1;
  piVar7 = piVar7 + 2;
  if (1 < iVar12) goto code_r0x00507505;
  goto LAB_005074f7;
code_r0x00507505:
  pvStack_a50 = (void *)0x0;
  CParticleManager__Unk_004cb040(auStack_a54);
  uStack_4 = 0;
  CParticleManager__CreateEffect
            (local_a84[1],auStack_a54,DAT_00855040,DAT_00855044,DAT_00855048,DAT_0085504c,0,
             (*(byte *)(*(int *)((int)param_1 + 8) + 0x34) & 8) != 0);
  if ((pvStack_a50 != (void *)0x0) &&
     (CMonitor__Unk_004097a0(pvStack_a50,&local_a68,unaff_EDI), pvStack_a50 != (void *)0x0)) {
    puVar3 = auStack_7c0;
    puVar16 = (undefined4 *)((int)pvStack_a50 + 0x10);
    for (iVar12 = 0xc; iVar12 != 0; iVar12 = iVar12 + -1) {
      *puVar16 = *puVar3;
      puVar3 = puVar3 + 1;
      puVar16 = puVar16 + 1;
    }
    *(undefined4 *)((int)pvStack_a50 + 0xa0) = 1;
  }
  uStack_4 = 0xffffffff;
  CParticleManager__RemoveFromGlobalList();
LAB_00507652:
  piVar11 = local_a84;
  if (local_a84[0x2e] != -1) {
    CUnitAI__Unk_0044a610
              (&DAT_0089c9a0,(int)&local_a68,local_a84[0x2e],local_a84[0x2f],(int)unaff_EDI);
    piVar11 = local_a84;
  }
LAB_00507680:
  if ((*piVar11 != 0) && (piVar7 = (int *)OID__CreateObject(0x15,0), piVar7 != (int *)0x0)) {
    CInfluenceMap__Init();
    uStack_3c4 = local_a68;
    uStack_3c0 = uStack_a64;
    uStack_3b8 = uStack_a5c;
    fStack_3bc = fStack_a60;
    CUnit__Unk_004df530(piVar7,*piVar11,unaff_EDI);
    puVar20 = auStack_3c8;
    (**(code **)(*piVar7 + 0x24))();
    uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar8 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar9 = Random__NextLCGAbs(DAT_008a9d9c);
    local_a80 = ((float)(uVar4 & 400) * _DAT_005dfca4 - _DAT_005d8cb8) + _DAT_005d8578;
    fStack_a7c = ((float)(uVar8 & 400) * _DAT_005dfca4 - _DAT_005d8cb8) + _DAT_005d8578;
    fStack_a78 = ((float)(uVar9 & 400) * _DAT_005dfca4 - _DAT_005d8cb8) - _DAT_005d85c0;
    CUnitAI__Unk_0044a930(param_1,(int)local_3fc,puVar20);
    fStack_978 = local_a80 * *extraout_EAX +
                 fStack_a7c * extraout_EAX[1] + fStack_a78 * extraout_EAX[2];
    fStack_974 = local_a80 * extraout_EAX[4] +
                 fStack_a7c * extraout_EAX[5] + fStack_a78 * extraout_EAX[6];
    fStack_a78 = local_a80 * extraout_EAX[8] +
                 fStack_a7c * extraout_EAX[9] + fStack_a78 * extraout_EAX[10];
    fStack_a74 = fStack_96c;
    local_a80 = fStack_978;
    fStack_a7c = fStack_974;
    fStack_970 = fStack_a78;
    (**(code **)(**(int **)((int)param_1 + 8) + 0x6c))(afStack_8ec + 1);
    local_a84 = (int *)((float)local_a84 + afStack_8ec[0]);
    local_a80 = afStack_8ec[1] + local_a80;
    fStack_a7c = afStack_8ec[2] + fStack_a7c;
    (**(code **)(*piVar7 + 0x70))(&local_a84);
    piVar11 = local_a84;
  }
  if ((*(byte *)((int)*(void **)((int)param_1 + 8) + 0x34) & 8) != 0) {
    CGeneralVolume__Unk_0040c340(*(void **)((int)param_1 + 8),param_1,(int)unaff_EDI);
  }
  iVar12 = 1;
LAB_0050787d:
  local_a4c = local_a4c + 1;
  unaff_ESI = piVar22;
  if (piVar11[0x12] <= local_a4c) {
    ExceptionList = local_c;
    return iVar12;
  }
  goto LAB_00506aaa;
}
