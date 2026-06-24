/* address: 0x0054c920 */
/* name: CDXMeshVB__BuildSkeletalVB */
/* signature: undefined CDXMeshVB__BuildSkeletalVB(void) */


/* WARNING: Type propagation algorithm not settling */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CDXMeshVB__BuildSkeletalVB(int param_1)

{
  void *obj;
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  int extraout_EAX;
  float *pfVar6;
  int *piVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  int *piVar11;
  undefined1 *puVar12;
  int iVar13;
  undefined4 *local_228;
  int local_224;
  int *local_220;
  undefined4 *local_21c;
  undefined4 *local_218;
  int local_214;
  undefined4 *local_210;
  undefined4 *local_20c;
  int local_208;
  undefined4 *local_204;
  uint auStack_200 [64];
  int local_100 [64];

  *(undefined4 *)(param_1 + 0x108) = 0;
  CConsole__Status(&DAT_00663498,s_Building_skeletal_VB_00651290);
  iVar10 = *(int *)(*(int *)(param_1 + 0x10c) + 0xa8);
  local_21c = *(undefined4 **)(*(int *)(param_1 + 0x10c) + 0xb0);
  local_214 = iVar10;
  puVar3 = (undefined4 *)
           OID__AllocObject(iVar10 * 0xc00,0x3a,s_C__dev_ONSLAUGHT2_DXMeshVB_cpp_00651244,0x1a9);
  if (puVar3 == (undefined4 *)0x0) {
    puVar3 = (undefined4 *)0x0;
  }
  else {
    local_218 = (undefined4 *)(iVar10 * 0x40 + -1);
  }
  local_210 = puVar3;
  local_20c = (undefined4 *)
              OID__AllocObject(iVar10 * 0x180,0x3a,s_C__dev_ONSLAUGHT2_DXMeshVB_cpp_00651244,0x1aa);
  OID__AllocObject(iVar10 * 2,0x3a,s_C__dev_ONSLAUGHT2_DXMeshVB_cpp_00651244,0x1ab);
  CVertexShader__Unk_005019d0();
  if (0 < iVar10) {
    local_204 = puVar3 + 8;
    local_224 = 0;
    local_218 = (undefined4 *)iVar10;
    do {
      local_228 = (undefined4 *)0x0;
      puVar3 = (undefined4 *)(*(int *)(*(int *)(param_1 + 0x10c) + 0x134) + local_224);
      if (0 < *(int *)(param_1 + 0x108)) {
        piVar11 = (int *)(param_1 + 8);
        do {
          local_220 = (int *)0x1;
          piVar7 = puVar3 + 0xc;
          local_208 = 6;
          do {
            iVar10 = *piVar7;
            if (((iVar10 == -1) ||
                (iVar13 = **(int **)(*(int *)(param_1 + 0x10c) + 0x128),
                piVar1 = (int *)(iVar13 + iVar10 * 0x24),
                *(float *)(iVar13 + 0x20 + iVar10 * 0x24) <= _DAT_005d856c)) || (*piVar1 == 0)) {
              if (*(int *)(*piVar11 + (-0x10 - (int)puVar3) + (int)piVar7) != 0) goto LAB_0054ca74;
            }
            else if (*(int **)(*piVar11 + (-0x10 - (int)puVar3) + (int)piVar7) != piVar1) {
LAB_0054ca74:
              local_220 = (int *)0x0;
            }
            piVar7 = piVar7 + 1;
            local_208 = local_208 + -1;
          } while (local_208 != 0);
          local_208 = 0;
          if (local_220 != (int *)0x0) break;
          local_228 = (undefined4 *)((int)local_228 + 1);
          piVar11 = piVar11 + 1;
        } while ((int)local_228 < *(int *)(param_1 + 0x108));
      }
      if (local_228 == (undefined4 *)*(int *)(param_1 + 0x108)) {
        puVar4 = (undefined4 *)
                 OID__AllocObject(0x3c,0x3a,s_C__dev_ONSLAUGHT2_DXMeshVB_cpp_00651244,0x1d8);
        if (puVar4 == (undefined4 *)0x0) {
          puVar4 = (undefined4 *)0x0;
        }
        else {
          *puVar4 = 0;
          puVar4[1] = 0;
        }
        iVar10 = 6;
        *(undefined4 **)(param_1 + 8 + *(int *)(param_1 + 0x108) * 4) = puVar4;
        *(undefined4 *)(*(int *)(param_1 + 8 + *(int *)(param_1 + 0x108) * 4) + 0x14) = 0;
        *(undefined4 *)(*(int *)(param_1 + 8 + *(int *)(param_1 + 0x108) * 4) + 0x10) = 0;
        *(undefined4 *)(*(int *)(param_1 + 8 + *(int *)(param_1 + 0x108) * 4) + 0x18) = 0;
        piVar11 = puVar3 + 0xc;
        do {
          iVar13 = *piVar11;
          if (((iVar13 == -1) ||
              (iVar5 = **(int **)(*(int *)(param_1 + 0x10c) + 0x128),
              piVar7 = (int *)(iVar5 + iVar13 * 0x24),
              *(float *)(iVar5 + 0x20 + iVar13 * 0x24) <= _DAT_005d856c)) || (*piVar7 == 0)) {
            *(undefined4 *)
             ((int)piVar11 +
             (-0x10 - (int)puVar3) + *(int *)(param_1 + 8 + *(int *)(param_1 + 0x108) * 4)) = 0;
          }
          else {
            *(int **)((int)piVar11 +
                     (-0x10 - (int)puVar3) + *(int *)(param_1 + 8 + *(int *)(param_1 + 0x108) * 4))
                 = piVar7;
          }
          piVar11 = piVar11 + 1;
          iVar10 = iVar10 + -1;
        } while (iVar10 != 0);
        *(int *)(param_1 + 0x108) = *(int *)(param_1 + 0x108) + 1;
      }
      puVar4 = (undefined4 *)(**(int **)(*(int *)(param_1 + 0x10c) + 0x84) + puVar3[8] * 0x10);
      local_204[-8] = *puVar4;
      local_204[-7] = puVar4[1];
      local_204[-6] = puVar4[2];
      local_204[1] = puVar3[0xb];
      local_204[2] = puVar3[9];
      local_204[3] = puVar3[10];
      local_204[-2] = *puVar3;
      local_204[-1] = puVar3[1];
      *local_204 = puVar3[2];
      iVar10 = 0;
      pfVar6 = (float *)(local_204 + -5);
      do {
        iVar10 = iVar10 + 4;
        *pfVar6 = (float)*(int *)(*(int *)(*(int *)(*(int *)(param_1 + 0x10c) + 0xd8) +
                                          puVar3[8] * 4) + -4 + iVar10) * _DAT_005d8cc0;
        pfVar6 = pfVar6 + 1;
      } while (iVar10 < 0xc);
      local_224 = local_224 + 0x60;
      local_204 = local_204 + 0xc;
      local_218 = (undefined4 *)((int)local_218 + -1);
    } while (local_218 != (undefined4 *)0x0);
    local_218 = (undefined4 *)0x0;
  }
  CDXMeshVB__Helper_0056eb60(0x18);
  CDXMeshVB__Helper_0056eb70(1);
  CDXMeshVB__Helper_0056eb80(0);
  CDXMeshVB__Helper_0056eb50(0);
  iVar10 = 0;
  if (0 < *(int *)(param_1 + 0x108)) {
    piVar11 = (int *)(param_1 + 8);
    do {
      iVar10 = iVar10 + 1;
      *(undefined4 *)(*piVar11 + 0x10) = 0;
      *(undefined4 *)(*piVar11 + 0x18) = 0;
      piVar11 = piVar11 + 1;
    } while (iVar10 < *(int *)(param_1 + 0x108));
  }
  iVar10 = 0;
  if (0 < *(int *)(param_1 + 0x108)) {
    iVar13 = (int)local_21c * 6;
    do {
      iVar5 = OID__AllocObject(iVar13,0x3a,s_C__dev_ONSLAUGHT2_DXMeshVB_cpp_00651244,0x216);
      local_100[iVar10] = iVar5;
      iVar5 = *(int *)(param_1 + 0x108);
      auStack_200[iVar10] = 0;
      iVar10 = iVar10 + 1;
    } while (iVar10 < iVar5);
  }
  if (0 < (int)local_21c) {
    local_228 = (undefined4 *)0x0;
    local_218 = local_21c;
    do {
      iVar10 = 0;
      piVar11 = (int *)(*(int *)(*(int *)(param_1 + 0x10c) + 0x80) + (int)local_228);
      if (0 < *(int *)(param_1 + 0x108)) {
        local_220 = (int *)(param_1 + 8);
        do {
          local_224 = 1;
          iVar13 = -0x10 - *piVar11;
          piVar7 = (int *)(*piVar11 + 0x30);
          local_21c = (undefined4 *)0x6;
          do {
            iVar5 = *piVar7;
            if (((iVar5 == -1) ||
                (iVar2 = **(int **)(*(int *)(param_1 + 0x10c) + 0x128),
                piVar1 = (int *)(iVar2 + iVar5 * 0x24),
                *(float *)(iVar2 + 0x20 + iVar5 * 0x24) <= _DAT_005d856c)) || (*piVar1 == 0)) {
              if (*(int *)(*local_220 + iVar13 + (int)piVar7) != 0) goto LAB_0054cd57;
            }
            else if (*(int **)(*local_220 + iVar13 + (int)piVar7) != piVar1) {
LAB_0054cd57:
              local_224 = 0;
            }
            piVar7 = piVar7 + 1;
            local_21c = (undefined4 *)((int)local_21c + -1);
          } while (local_21c != (undefined4 *)0x0);
          local_21c = (undefined4 *)0x0;
          if (local_224 != 0) break;
          iVar10 = iVar10 + 1;
          local_220 = local_220 + 1;
        } while (iVar10 < *(int *)(param_1 + 0x108));
      }
      iVar13 = local_100[iVar10];
      iVar5 = *piVar11 - *(int *)(*(int *)(param_1 + 0x10c) + 0x134);
      uVar8 = auStack_200[iVar10] + 3;
      auStack_200[iVar10] = uVar8;
      *(short *)(iVar13 + -6 + uVar8 * 2) =
           ((short)(iVar5 / 0x60) + (short)(iVar5 >> 0x1f)) -
           (short)((longlong)iVar5 * 0x2aaaaaab >> 0x3f);
      iVar5 = piVar11[1] - *(int *)(*(int *)(param_1 + 0x10c) + 0x134);
      *(short *)(iVar13 + -4 + uVar8 * 2) =
           ((short)(iVar5 / 0x60) + (short)(iVar5 >> 0x1f)) -
           (short)((longlong)iVar5 * 0x2aaaaaab >> 0x3f);
      iVar5 = piVar11[2] - *(int *)(*(int *)(param_1 + 0x10c) + 0x134);
      *(short *)(iVar13 + -2 + uVar8 * 2) =
           ((short)(iVar5 / 0x60) + (short)(iVar5 >> 0x1f)) -
           (short)((longlong)iVar5 * 0x2aaaaaab >> 0x3f);
      iVar10 = *(int *)(param_1 + 8 + iVar10 * 4);
      local_228 = (undefined4 *)((int)local_228 + 0xc);
      *(int *)(iVar10 + 0x10) = *(int *)(iVar10 + 0x10) + 1;
      local_218 = (undefined4 *)((int)local_218 + -1);
    } while (local_218 != (undefined4 *)0x0);
  }
  local_228 = (undefined4 *)0x0;
  if (0 < *(int *)(param_1 + 0x108)) {
    puVar12 = (undefined1 *)0x0;
    piVar11 = (int *)(param_1 + 8);
    local_21c = (undefined4 *)(local_214 * 6);
    do {
      CDXMeshVB__Helper_0056eb90
                ((void *)local_100[(int)local_228],auStack_200[(int)local_228],&local_224,&local_220
                );
      iVar10 = 0;
      *(undefined4 *)(*piVar11 + 0x10) = 0;
      if (0 < *(int *)(local_224 + 4)) {
        do {
          *(undefined2 *)((int)local_20c + (int)(puVar12 + *(int *)(*piVar11 + 0x10)) * 2) =
               *(undefined2 *)(*(int *)(local_224 + 8) + iVar10 * 2);
          iVar10 = iVar10 + 1;
          *(int *)(*piVar11 + 0x10) = *(int *)(*piVar11 + 0x10) + 1;
        } while (iVar10 < *(int *)(local_224 + 4));
      }
      *(int *)(*piVar11 + 0x18) = *(int *)(*piVar11 + 0x10) + -2;
      if (local_224 != 0) {
        obj = (void *)(local_224 + -4);
        CDXLandscape__Helper_0055db0a
                  (local_224,0xc,*(int *)(local_224 + -4),CLandscapeTexture__FreeTexture);
        OID__FreeObject(obj);
      }
      local_228 = (undefined4 *)((int)local_228 + 1);
      piVar11 = piVar11 + 1;
      puVar12 = puVar12 + (int)local_21c;
    } while ((int)local_228 < *(int *)(param_1 + 0x108));
  }
  iVar10 = 0;
  if (0 < *(int *)(param_1 + 0x108)) {
    piVar11 = local_100;
    do {
      OID__FreeObject((void *)*piVar11);
      iVar10 = iVar10 + 1;
      piVar11 = piVar11 + 1;
    } while (iVar10 < *(int *)(param_1 + 0x108));
  }
  local_220 = (int *)0x1;
  if (*(int *)(param_1 + 0x108) < 1) goto LAB_0054d05a;
  *(int *)(*(int *)(param_1 + 8) + 0x14) = local_214;
  iVar13 = 1;
  *(int *)(*(int *)(param_1 + 8) + 8) = *(int *)(*(int *)(param_1 + 8) + 0x14) * 0x30;
  iVar10 = 8;
  if (DAT_00854e6c != '\0') {
    iVar10 = 0x18;
    iVar13 = 2;
  }
  iVar10 = CEngine__DeviceCall68_CheckError
                     (&DAT_00855bb0,*(int *)(*(int *)(param_1 + 8) + 8),iVar10,0,iVar13,
                      *(int *)(param_1 + 8));
  if (iVar10 < 0) {
LAB_0054d015:
    local_220 = (int *)0x0;
  }
  else {
    DebugTrace((char *)&DAT_009c3df0);
    iVar10 = (**(code **)(*(int *)**(undefined4 **)(param_1 + 8) + 0x2c))
                       ((int *)**(undefined4 **)(param_1 + 8),0,0,&local_21c,0);
    if (iVar10 < 0) goto LAB_0054d015;
    puVar3 = local_210;
    puVar4 = local_21c;
    for (uVar8 = (uint)(local_214 * 0x30) >> 2; uVar8 != 0; uVar8 = uVar8 - 1) {
      *puVar4 = *puVar3;
      puVar3 = puVar3 + 1;
      puVar4 = puVar4 + 1;
    }
    for (iVar10 = 0; iVar10 != 0; iVar10 = iVar10 + -1) {
      *(undefined1 *)puVar4 = *(undefined1 *)puVar3;
      puVar3 = (undefined4 *)((int)puVar3 + 1);
      puVar4 = (undefined4 *)((int)puVar4 + 1);
    }
    (**(code **)(*(int *)**(undefined4 **)(param_1 + 8) + 0x30))
              ((int *)**(undefined4 **)(param_1 + 8));
  }
  iVar10 = 1;
  if (1 < *(int *)(param_1 + 0x108)) {
    piVar11 = (int *)(param_1 + 0xc);
    do {
      iVar10 = iVar10 + 1;
      *(undefined4 *)(*piVar11 + 8) = *(undefined4 *)(*(int *)(param_1 + 8) + 8);
      *(undefined4 *)*piVar11 = **(undefined4 **)(param_1 + 8);
      *(undefined4 *)(*piVar11 + 0x14) = *(undefined4 *)(*(int *)(param_1 + 8) + 0x14);
      piVar11 = piVar11 + 1;
    } while (iVar10 < *(int *)(param_1 + 0x108));
  }
LAB_0054d05a:
  local_224 = 0;
  if (0 < *(int *)(param_1 + 0x108)) {
    piVar11 = (int *)(param_1 + 8);
    local_218 = (undefined4 *)(local_214 * 0xc);
    local_228 = local_20c;
    do {
      iVar13 = 1;
      *(undefined4 *)(*piVar11 + 0x1c) = 1;
      iVar10 = *piVar11;
      if (*(int *)(iVar10 + 0x1c) != 0) {
        iVar5 = 8;
        if (DAT_00854e6c != '\0') {
          iVar5 = 0x18;
          iVar13 = 2;
        }
        *(int *)(iVar10 + 0xc) = *(int *)(iVar10 + 0x10) << 1;
        CEngine__DeviceCall6C(&DAT_00855bb0,*(int *)(*piVar11 + 0xc),iVar5,0x65,iVar13,*piVar11 + 4)
        ;
        if (-1 < extraout_EAX) {
          DebugTrace((char *)&DAT_009c3df0);
          iVar10 = (**(code **)(**(int **)(*piVar11 + 4) + 0x2c))
                             (*(int **)(*piVar11 + 4),0,0,&local_21c,0);
          if (-1 < iVar10) {
            uVar9 = *(int *)(*piVar11 + 0x10) << 1;
            puVar3 = local_228;
            puVar4 = local_21c;
            for (uVar8 = uVar9 >> 2; uVar8 != 0; uVar8 = uVar8 - 1) {
              *puVar4 = *puVar3;
              puVar3 = puVar3 + 1;
              puVar4 = puVar4 + 1;
            }
            for (uVar9 = uVar9 & 3; uVar9 != 0; uVar9 = uVar9 - 1) {
              *(undefined1 *)puVar4 = *(undefined1 *)puVar3;
              puVar3 = (undefined4 *)((int)puVar3 + 1);
              puVar4 = (undefined4 *)((int)puVar4 + 1);
            }
            (**(code **)(**(int **)(*piVar11 + 4) + 0x30))(*(int **)(*piVar11 + 4));
            goto LAB_0054d156;
          }
        }
        local_220 = (int *)0x0;
      }
LAB_0054d156:
      local_224 = local_224 + 1;
      piVar11 = piVar11 + 1;
      local_228 = (undefined4 *)((int)local_228 + (int)local_218);
    } while (local_224 < *(int *)(param_1 + 0x108));
  }
  *(undefined4 *)(param_1 + 0x114) = 0x30;
  *(undefined4 *)(param_1 + 0x118) = 0;
  *(undefined4 *)(param_1 + 0x11c) = 4;
  OID__FreeObject(local_20c);
  OID__FreeObject(local_210);
  piVar11 = local_220;
  CConsole__StatusDone(&DAT_00663498,s_Building_skeletal_VB_00651290,local_220 != (int *)0x0);
  return (-(uint)(piVar11 != (int *)0x0) & 0x7fffbffb) + 0x80004005;
}
