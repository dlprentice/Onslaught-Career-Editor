/* address: 0x004e3f90 */
/* name: CSpawnerThng__ProcessSpawnWave */
/* signature: undefined CSpawnerThng__ProcessSpawnWave(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CSpawnerThng__ProcessSpawnWave(void *param_1)

{
  float *pfVar1;
  char cVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int *this;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  undefined4 *puVar10;
  char *pcVar11;
  undefined4 *puVar12;
  char *pcVar13;
  float10 fVar14;
  float10 fVar15;
  float10 extraout_ST0;
  float10 fVar16;
  float fVar17;
  undefined **appuStack_3d0 [6];
  float fStack_3b8;
  float fStack_3a8;
  float fStack_398;
  float fStack_38c;
  float fStack_388;
  undefined4 uStack_33c;
  char acStack_324 [776];
  undefined4 uStack_1c;
  undefined4 uStack_18;
  void *pvStack_14;

  if (*(int *)((int)param_1 + 0x3ec) != 0) {
    puVar12 = (undefined4 *)((int)param_1 + 0x24);
    pfVar1 = (float *)((int)param_1 + 0x14);
    fVar17 = *(float *)((int)param_1 + 1000);
    (**(code **)(**(int **)((int)param_1 + 0x3d4) + 0x160))
              (fVar17,*(undefined4 *)((int)param_1 + 0x3e4),pfVar1,puVar12);
    if (((*pfVar1 == _DAT_005d856c) && (*(float *)((int)param_1 + 0x18) == _DAT_005d856c)) &&
       (*(float *)((int)param_1 + 0x1c) == _DAT_005d856c)) {
      *(undefined4 *)((int)param_1 + 0x3e4) = 1;
      (**(code **)(**(int **)((int)param_1 + 0x3d4) + 0x160))
                (*(undefined4 *)((int)param_1 + 1000),1,pfVar1,puVar12);
      if (((*pfVar1 == _DAT_005d856c) && (*(float *)((int)param_1 + 0x18) == _DAT_005d856c)) &&
         (*(float *)((int)param_1 + 0x1c) == _DAT_005d856c)) {
        iVar4 = *(int *)((int)param_1 + 0x3d4);
        *pfVar1 = *(float *)(iVar4 + 0x1c);
        *(undefined4 *)((int)param_1 + 0x18) = *(undefined4 *)(iVar4 + 0x20);
        *(undefined4 *)((int)param_1 + 0x1c) = *(undefined4 *)(iVar4 + 0x24);
        *(undefined4 *)((int)param_1 + 0x20) = *(undefined4 *)(iVar4 + 0x28);
        puVar10 = (undefined4 *)(iVar4 + 0x3c);
        for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
          *puVar12 = *puVar10;
          puVar10 = puVar10 + 1;
          puVar12 = puVar12 + 1;
        }
      }
    }
    iVar4 = (**(code **)(**(int **)((int)param_1 + 0x3d4) + 0x10c))();
    if (iVar4 == 0) {
      iVar6 = CUnit__GetGridMapByType(*(int *)((int)param_1 + 0x3d4));
      iVar5 = (int)(float)(longlong)ROUND(*pfVar1) >> 1;
      iVar7 = (int)(float)(longlong)ROUND(*(float *)((int)param_1 + 0x18)) >> 1;
      for (iVar4 = iVar7 + -1; iVar4 < iVar7 + 1; iVar4 = iVar4 + 1) {
        if (((-1 < iVar4) && (iVar4 < 0x100)) && (uVar9 = iVar5 - 1, (int)uVar9 < iVar5 + 1)) {
          do {
            if ((-1 < (int)uVar9) && ((int)uVar9 < 0x100)) {
              uVar8 = uVar9 & 0x80000007;
              if ((int)uVar8 < 0) {
                uVar8 = (uVar8 - 1 | 0xfffffff8) + 1;
              }
              if ((*(byte *)(((int)uVar9 >> 3) * 0x100 + iVar4 + iVar6) &
                  (byte)(1 << ((byte)uVar8 & 0x1f))) == 0) {
                iVar4 = CWorldPhysicsManager__Unk_00511440
                                  (*(void **)(*(int *)((int)param_1 + 0x3d0) + 4));
                if (iVar4 != 0) goto LAB_004e4382;
                goto LAB_004e4149;
              }
            }
            uVar9 = uVar9 + 1;
          } while ((int)uVar9 < iVar5 + 1);
        }
      }
    }
LAB_004e4149:
    iVar4 = CSpawnerThng__IsSpawnPositionClear(pfVar1);
    if ((iVar4 != 0) &&
       (this = (int *)CWorldPhysicsManager__CreateThingByType(*(undefined4 *)((int)param_1 + 0x3dc))
       , this != (int *)0x0)) {
      *(int *)((int)param_1 + 0x3e4) = *(int *)((int)param_1 + 0x3e4) + 1;
      CInfluenceMap__Init();
      appuStack_3d0[0] = &PTR_LAB_005dc1c0;
      pvStack_14 = (void *)0x0;
      VFuncSlot_00_0040e1b0(appuStack_3d0,(int)param_1 + 0x10,(int)fVar17);
      fVar14 = (float10)fStack_3b8;
      fVar15 = (float10)fStack_3a8;
      fVar16 = (float10)fpatan(fVar14,fVar15);
      pvStack_14 = *(void **)((int)param_1 + 0x3cc);
      fStack_38c = (float)-fVar16;
      if (SQRT(fVar14 * fVar14 + fVar15 * fVar15 + (float10)fStack_398 * (float10)fStack_398) <=
          (float10)_DAT_005d856c) {
        fVar14 = (float10)_DAT_005d856c;
      }
      else {
        OID__Helper_0055dcb0();
        fVar14 = extraout_ST0;
      }
      iVar4 = *(int *)((int)param_1 + 0x3dc);
      fStack_388 = (float)fVar14;
      uStack_33c = 0x3fc00000;
      iVar6 = 0;
      pvStack_14 = CSPtrSet__First(DAT_008553fc);
      while (pvStack_14 != (void *)0x0) {
        if (iVar6 == iVar4) goto LAB_004e425b;
        iVar6 = iVar6 + 1;
        piVar3 = *(int **)(*(int *)((int)DAT_008553fc + 8) + 4);
        *(int **)((int)DAT_008553fc + 8) = piVar3;
        if (piVar3 == (int *)0x0) {
          pvStack_14 = (void *)0x0;
        }
        else {
          pvStack_14 = (void *)*piVar3;
        }
      }
      pvStack_14 = (void *)0x0;
LAB_004e425b:
      uStack_1c = *(undefined4 *)((int)param_1 + 0x3d4);
      switch(*(undefined4 *)((int)param_1 + 1000)) {
      case 10:
        uStack_18 = 0xf;
        break;
      case 0xb:
        uStack_18 = 0x10;
        break;
      case 0xc:
        uStack_18 = 0x11;
        break;
      case 0xd:
        uStack_18 = 0x12;
        break;
      case 0xe:
        uStack_18 = 0x13;
      }
      if (*(int *)((int)param_1 + 0x3c0) != 0) {
        uVar9 = 0xffffffff;
        pcVar11 = (char *)((int)param_1 + 700);
        do {
          pcVar13 = pcVar11;
          if (uVar9 == 0) break;
          uVar9 = uVar9 - 1;
          pcVar13 = pcVar11 + 1;
          cVar2 = *pcVar11;
          pcVar11 = pcVar13;
        } while (cVar2 != '\0');
        uVar9 = ~uVar9;
        pcVar11 = pcVar13 + -uVar9;
        pcVar13 = acStack_324;
        for (uVar8 = uVar9 >> 2; uVar8 != 0; uVar8 = uVar8 - 1) {
          *(undefined4 *)pcVar13 = *(undefined4 *)pcVar11;
          pcVar11 = pcVar11 + 4;
          pcVar13 = pcVar13 + 4;
        }
        for (uVar9 = uVar9 & 3; uVar9 != 0; uVar9 = uVar9 - 1) {
          *pcVar13 = *pcVar11;
          pcVar11 = pcVar11 + 1;
          pcVar13 = pcVar13 + 1;
        }
      }
      (**(code **)(*this + 0x24))(appuStack_3d0);
      CSpawnerThng__Helper_004fc3a0(this,*(int *)(*(int *)((int)param_1 + 0x3d0) + 0x1c),fVar17);
      if (*(int **)((int)param_1 + 8) != (int *)0x0) {
        (**(code **)(**(int **)((int)param_1 + 8) + 0x10c))(&stack0xfffffc20,this,0,0);
      }
      iVar4 = *(int *)((int)param_1 + 0xc) + 1;
      *(int *)((int)param_1 + 0xc) = iVar4;
      if (*(int *)(*(int *)((int)param_1 + 0x3d0) + 0x10) <= iVar4) {
        iVar4 = *(int *)((int)param_1 + 8);
        if (iVar4 != 0) {
          *(undefined4 *)(iVar4 + 0x80) = 0;
        }
        CGenericActiveReader__SetReader((int *)((int)param_1 + 8),(void *)0x0);
        fVar17 = DAT_00672fd0 + *(float *)(*(int *)((int)param_1 + 0x3d0) + 0x20);
        *(undefined4 *)((int)param_1 + 0x3ec) = 0;
        *(float *)((int)param_1 + 0x3e0) = fVar17;
        return;
      }
    }
LAB_004e4382:
    CEventManager__AddEvent_AtTime
              (&EVENT_MANAGER,3000,param_1,(float *)&stack0xfffffc20,0,(void *)0x0,(void *)0x0);
  }
  return;
}
