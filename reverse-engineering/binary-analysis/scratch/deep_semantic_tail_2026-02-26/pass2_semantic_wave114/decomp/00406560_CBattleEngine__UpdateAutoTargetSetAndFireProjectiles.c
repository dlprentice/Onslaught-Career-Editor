/* address: 0x00406560 */
/* name: CBattleEngine__UpdateAutoTargetSetAndFireProjectiles */
/* signature: void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(int param_1)

{
  void *this;
  float10 fVar1;
  float fVar2;
  bool bVar3;
  int iVar4;
  void *this_00;
  int *piVar5;
  undefined3 extraout_var;
  int *piVar6;
  undefined3 extraout_var_00;
  int iVar7;
  int iVar8;
  undefined4 *puVar9;
  int unaff_EDI;
  undefined4 *puVar10;
  float10 fVar11;
  float10 fVar12;
  double dVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  float local_40;
  float local_3c;
  float local_38;
  undefined4 local_30 [4];
  undefined4 local_20;
  undefined4 local_10;

  if (*(int *)(param_1 + 0x260) == 3) {
    iVar4 = CVBufTexture_Unk_0050a290__Wrapper_00414b30(*(void **)(param_1 + 0x57c));
  }
  else {
    iVar4 = CVBufTexture_Unk_0050a290__Wrapper_00414b30(*(void **)(param_1 + 0x578));
  }
  if (iVar4 == 0) {
    if (*(int *)(param_1 + 0x260) == 3) {
      this_00 = (void *)CBattleEngine__GetIndexedEntry(*(void **)(param_1 + 0x57c));
      iVar4 = CBattleEngine__IsIndexedEntryUsable(*(void **)(param_1 + 0x57c));
    }
    else {
      this_00 = (void *)CGeneralVolume__ResolveCurrentOrFallbackEntry(*(void **)(param_1 + 0x578));
      iVar4 = CBattleEngine__IsResolvedEntryUsable(*(void **)(param_1 + 0x578));
    }
    if (this_00 != (void *)0x0) {
      puVar9 = *(undefined4 **)(param_1 + 0x294);
      *(undefined4 **)(param_1 + 0x29c) = puVar9;
      if (puVar9 == (undefined4 *)0x0) {
        piVar5 = (int *)0x0;
      }
      else {
        piVar5 = (int *)*puVar9;
      }
      while (piVar5 != (int *)0x0) {
        iVar8 = *piVar5;
        if (iVar8 == 0) {
          CSPtrSet__Remove((undefined4 *)(param_1 + 0x294),piVar5);
          if (piVar5 != (int *)0x0) {
            CGenericActiveReader__dtor(piVar5);
            OID__FreeObject(piVar5);
          }
          puVar9 = *(undefined4 **)(param_1 + 0x294);
          *(undefined4 **)(param_1 + 0x29c) = puVar9;
          if (puVar9 == (undefined4 *)0x0) {
LAB_004067a4:
            piVar5 = (int *)0x0;
          }
          else {
            piVar5 = (int *)*puVar9;
          }
        }
        else {
          puVar9 = (undefined4 *)(param_1 + 0x3c);
          puVar10 = local_30;
          for (iVar7 = 0xc; uVar15 = local_20, uVar14 = local_30[2], iVar7 != 0; iVar7 = iVar7 + -1)
          {
            *puVar10 = *puVar9;
            puVar9 = puVar9 + 1;
            puVar10 = puVar10 + 1;
          }
          local_20 = local_30[1];
          local_30[2] = local_10;
          local_10 = uVar14;
          local_30[1] = uVar15;
          Vec3__SetXYZ();
          fVar2 = SQRT(local_40 * local_40 + local_38 * local_38 + local_3c * local_3c);
          if (fVar2 != _DAT_005d856c) {
            fVar2 = _DAT_005d8568 / fVar2;
            local_40 = fVar2 * local_40;
            local_3c = fVar2 * local_3c;
            local_38 = local_38 * fVar2;
          }
          dVar13 = CBattleEngine__Helper_00506620((int)this_00);
          fVar11 = (float10)fcos((float10)dVar13);
          if ((((float10)local_3c < fVar11) || (iVar4 == 0)) || ((*(byte *)(iVar8 + 0x2c) & 4) != 0)
             ) {
            CSPtrSet__Remove((undefined4 *)(param_1 + 0x294),piVar5);
            if (piVar5 != (int *)0x0) {
              CGenericActiveReader__dtor(piVar5);
              OID__FreeObject(piVar5);
            }
            puVar9 = *(undefined4 **)(param_1 + 0x294);
            *(undefined4 **)(param_1 + 0x29c) = puVar9;
            if (puVar9 == (undefined4 *)0x0) goto LAB_004067a4;
            piVar5 = (int *)*puVar9;
          }
        }
        if (piVar5 == (int *)0x0) break;
        puVar9 = *(undefined4 **)(*(int *)(param_1 + 0x29c) + 4);
        *(undefined4 **)(param_1 + 0x29c) = puVar9;
        if (puVar9 == (undefined4 *)0x0) {
          piVar5 = (int *)0x0;
        }
        else {
          piVar5 = (int *)*puVar9;
        }
      }
      this = (void *)(param_1 + 0x294);
      iVar8 = 0;
      piVar5 = CSPtrSet__First(this);
      while (piVar5 != (int *)0x0) {
        if (*piVar5 != 0) {
          iVar8 = iVar8 + 1;
        }
        piVar5 = CSPtrSet__Next(this);
      }
      iVar7 = CBattleEngine__Helper_00506350((int)this_00);
      if (((iVar8 < iVar7) && (iVar4 != 0)) &&
         (iVar4 = CUnit__Helper_00509f70((int)this_00), iVar4 != 0)) {
        iVar4 = CBattleEngine__Helper_00506530((int)this_00);
        fVar2 = DAT_00672fd0;
        if (iVar4 == 0) {
          piVar5 = *(int **)(param_1 + 0x4c8);
          if ((piVar5 != (int *)0x0) ||
             (piVar5 = (int *)CBattleEngine__Helper_0040acc0
                                        ((void *)param_1,(void *)0x0,(void *)0x0,0,unaff_EDI),
             piVar5 != (int *)0x0)) {
            piVar6 = CSPtrSet__First(this);
            while (piVar6 != (int *)0x0) {
              if ((int *)*piVar6 == piVar5) {
                return;
              }
              piVar6 = CSPtrSet__Next(this);
            }
            iVar4 = CBattleEngine__Helper_004fd3d0((void *)param_1,piVar5[0x4e],unaff_EDI);
            if ((iVar4 != 0) &&
               (bVar3 = CBattleEngine__Helper_005061f0(this_00,(int)piVar5,unaff_EDI),
               CONCAT31(extraout_var_00,bVar3) != 0)) {
              local_40 = (float)piVar5[7] - *(float *)(param_1 + 0x1c);
              iVar4 = *piVar5;
              local_3c = (float)piVar5[8] - *(float *)(param_1 + 0x20);
              puVar9 = (undefined4 *)(param_1 + 0x3c);
              puVar10 = local_30;
              for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
                *puVar10 = *puVar9;
                puVar9 = puVar9 + 1;
                puVar10 = puVar10 + 1;
              }
              local_38 = (float)piVar5[9] - *(float *)(param_1 + 0x24);
              fVar12 = (float10)(**(code **)(iVar4 + 0x16c))();
              fVar11 = (float10)_DAT_005d85fc;
              fVar1 = (float10)_DAT_005d8568;
              dVar13 = CBattleEngine__Helper_00506710((int)this_00);
              dVar13 = dVar13 * (double)(float)(fVar1 - fVar12 * fVar11);
              if ((double)local_38 * (double)local_38 +
                  (double)local_3c * (double)local_3c + (double)local_40 * (double)local_40 <
                  dVar13 * dVar13) {
                local_30[2] = local_10;
                local_30[1] = local_20;
                Vec3__SetXYZ();
                fVar2 = SQRT(local_40 * local_40 + local_38 * local_38 + local_3c * local_3c);
                if (fVar2 != _DAT_005d856c) {
                  fVar2 = _DAT_005d8568 / fVar2;
                  local_40 = fVar2 * local_40;
                  local_3c = fVar2 * local_3c;
                  local_38 = local_38 * fVar2;
                }
                dVar13 = CBattleEngine__Helper_00506620((int)this_00);
                fVar11 = (float10)fcos((float10)dVar13);
                if (fVar11 < (float10)local_3c) {
                  uVar14 = 1;
                  dVar13 = CBattleEngine__Helper_00506440((int)this_00);
                  CBattleEngine__AddProjectile(piVar5,(float)dVar13,uVar14);
                }
              }
            }
          }
        }
        else if (iVar4 == 1) {
          CBattleEngine__Helper_00506710((int)this_00);
          iVar4 = CBattleEngine__SelectNearestForwardTargetFromGlobalSet();
          if (iVar4 != 0) {
            while( true ) {
              uVar14 = 0;
              dVar13 = CBattleEngine__Helper_00506440((int)this_00);
              CBattleEngine__AddProjectile(iVar4,(float)dVar13,uVar14);
              iVar4 = 0;
              piVar5 = CSPtrSet__First(this);
              while (piVar5 != (int *)0x0) {
                if (*piVar5 != 0) {
                  iVar4 = iVar4 + 1;
                }
                piVar5 = CSPtrSet__Next(this);
              }
              iVar8 = CBattleEngine__Helper_00506350((int)this_00);
              if (iVar8 <= iVar4) break;
              CBattleEngine__Helper_00506710((int)this_00);
              iVar4 = CBattleEngine__SelectNearestForwardTargetFromGlobalSet();
              if (iVar4 == 0) {
                return;
              }
            }
          }
        }
        else if (iVar4 == 2) {
          piVar5 = CSPtrSet__First(this);
          while (piVar5 != (int *)0x0) {
            if ((*piVar5 != 0) && (fVar2 < (float)piVar5[2])) {
              return;
            }
            piVar5 = CSPtrSet__Next(this);
          }
          bVar3 = false;
          piVar5 = CSPtrSet__First(this);
          if (((piVar5 != (int *)0x0) && (piVar5[4] != 0)) && (*piVar5 != 0)) {
            CBattleEngine__Helper_00506800((int)this_00);
            iVar4 = CBattleEngine__SelectNearestForwardTargetFromGlobalSet();
            if (iVar4 != 0) {
              uVar14 = 0;
              dVar13 = CBattleEngine__Helper_00506440((int)this_00);
              CBattleEngine__AddProjectile(iVar4,(float)dVar13,uVar14);
              bVar3 = true;
            }
          }
          if (((*(int *)(param_1 + 0x4c8) != 0) && (!bVar3)) &&
             ((iVar4 = CBattleEngine__Helper_004fd3d0
                                 ((void *)param_1,*(int *)(*(int *)(param_1 + 0x4c8) + 0x138),
                                  unaff_EDI), iVar4 != 0 &&
              (bVar3 = CBattleEngine__Helper_005061f0(this_00,*(int *)(param_1 + 0x4c8),unaff_EDI),
              CONCAT31(extraout_var,bVar3) != 0)))) {
            iVar4 = *(int *)(param_1 + 0x4c8);
            local_40 = *(float *)(iVar4 + 0x1c) - *(float *)(param_1 + 0x1c);
            puVar9 = (undefined4 *)(param_1 + 0x3c);
            puVar10 = local_30;
            for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
              *puVar10 = *puVar9;
              puVar9 = puVar9 + 1;
              puVar10 = puVar10 + 1;
            }
            local_3c = *(float *)(iVar4 + 0x20) - *(float *)(param_1 + 0x20);
            local_38 = *(float *)(iVar4 + 0x24) - *(float *)(param_1 + 0x24);
            dVar13 = CBattleEngine__Helper_00506710((int)this_00);
            if ((double)local_40 * (double)local_40 +
                (double)local_38 * (double)local_38 + (double)local_3c * (double)local_3c <
                dVar13 * dVar13) {
              local_30[2] = local_10;
              local_30[1] = local_20;
              Vec3__SetXYZ();
              SQRT__Wrapper_00406d50(&local_40);
              dVar13 = CBattleEngine__Helper_00506620((int)this_00);
              fVar11 = (float10)fcos((float10)dVar13);
              if (fVar11 < (float10)local_3c) {
                uVar14 = *(undefined4 *)(param_1 + 0x4c8);
                uVar15 = 1;
                dVar13 = CBattleEngine__Helper_00506440((int)this_00);
                CBattleEngine__AddProjectile(uVar14,(float)dVar13,uVar15);
                return;
              }
            }
          }
        }
      }
    }
  }
  return;
}
