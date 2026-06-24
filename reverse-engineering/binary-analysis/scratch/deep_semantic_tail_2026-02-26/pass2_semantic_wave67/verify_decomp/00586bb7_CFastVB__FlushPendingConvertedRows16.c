/* address: 0x00586bb7 */
/* name: CFastVB__FlushPendingConvertedRows16 */
/* signature: int __fastcall CFastVB__FlushPendingConvertedRows16(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CFastVB__FlushPendingConvertedRows16(int param_1)

{
  float *pfVar1;
  float *pfVar2;
  int iVar3;
  uint uVar4;
  float *pfVar5;
  int iVar6;
  ushort *puVar7;
  int iVar8;
  undefined2 in_FPUControlWord;
  undefined4 local_14;
  int local_c;

  if (*(int *)(param_1 + 0x1094) == 0) {
    return 0;
  }
  if (*(int *)(param_1 + 0x1098) == 0) {
    return 0;
  }
  puVar7 = (ushort *)
           (*(int *)(param_1 + 0x1088) * *(int *)(param_1 + 0x105c) +
            *(int *)(param_1 + 0x107c) * *(int *)(param_1 + 0x1058) + *(int *)(param_1 + 0x1078) * 2
           + *(int *)(param_1 + 0x20));
  pfVar5 = *(float **)(param_1 + 0x1074);
  local_14 = CONCAT22(local_14._2_2_,in_FPUControlWord);
  DAT_009d0c58 = local_14;
  iVar3 = *(int *)(param_1 + 4);
  if (iVar3 != 0x32595559) {
    if ((iVar3 == 0x42475247) || (iVar3 == 0x47424752)) {
      for (uVar4 = *(uint *)(param_1 + 0x1078); uVar4 < *(uint *)(param_1 + 0x1080);
          uVar4 = uVar4 + 2) {
        *puVar7 = (ushort)((int)ROUND(pfVar5[1] * _DAT_005e9f08 + _DAT_005e72d4) <<
                          ((byte)*(undefined4 *)(param_1 + 0x109c) & 0x1f)) |
                  (ushort)((int)ROUND(*pfVar5 * _DAT_005e9f08 + _DAT_005e72d4) <<
                          ((byte)*(undefined4 *)(param_1 + 0x10a0) & 0x1f));
        pfVar1 = pfVar5 + 5;
        pfVar2 = pfVar5 + 2;
        pfVar5 = pfVar5 + 8;
        puVar7[1] = (ushort)((int)ROUND(*pfVar1 * _DAT_005e9f08 + _DAT_005e72d4) <<
                            ((byte)*(undefined4 *)(param_1 + 0x109c) & 0x1f)) |
                    (ushort)((int)ROUND(*pfVar2 * _DAT_005e9f08 + _DAT_005e72d4) <<
                            ((byte)*(undefined4 *)(param_1 + 0x10a0) & 0x1f));
        puVar7 = puVar7 + 2;
      }
      goto LAB_00586ead;
    }
    if (iVar3 != 0x59565955) goto LAB_00586ead;
  }
  for (uVar4 = *(uint *)(param_1 + 0x1078); uVar4 < *(uint *)(param_1 + 0x1080); uVar4 = uVar4 + 2)
  {
    iVar3 = (int)ROUND(*pfVar5 * _DAT_005ea194 +
                       pfVar5[2] * _DAT_005ea190 + pfVar5[1] * _DAT_005ea18c + _DAT_005e72d4) + 0x10
    ;
    iVar8 = (int)ROUND(pfVar5[5] * _DAT_005ea18c +
                       pfVar5[6] * _DAT_005ea190 + pfVar5[4] * _DAT_005ea194 + _DAT_005e72d4) + 0x10
    ;
    iVar6 = (int)ROUND(((pfVar5[2] * _DAT_005ea188 - pfVar5[1] * _DAT_005ea184) -
                       *pfVar5 * _DAT_005ea180) + _DAT_005e72d4) + 0x80;
    local_c = (int)ROUND((*pfVar5 * _DAT_005ea188 -
                         (pfVar5[2] * _DAT_005ea178 + pfVar5[1] * _DAT_005ea17c)) + _DAT_005e72d4) +
              0x80;
    if (iVar3 < 0) {
      iVar3 = 0;
    }
    else if (0xff < iVar3) {
      iVar3 = 0xff;
    }
    if (iVar8 < 0) {
      iVar8 = 0;
    }
    else if (0xff < iVar8) {
      iVar8 = 0xff;
    }
    if (iVar6 < 0) {
      iVar6 = 0;
    }
    else if (0xff < iVar6) {
      iVar6 = 0xff;
    }
    if (local_c < 0) {
      local_c = 0;
    }
    else if (0xff < local_c) {
      local_c = 0xff;
    }
    pfVar5 = pfVar5 + 8;
    *puVar7 = (ushort)(iVar3 << ((byte)*(undefined4 *)(param_1 + 0x109c) & 0x1f)) |
              (ushort)(iVar6 << ((byte)*(undefined4 *)(param_1 + 0x10a0) & 0x1f));
    puVar7[1] = (ushort)(iVar8 << ((byte)*(undefined4 *)(param_1 + 0x109c) & 0x1f)) |
                (ushort)(local_c << ((byte)*(undefined4 *)(param_1 + 0x10a0) & 0x1f));
    puVar7 = puVar7 + 2;
  }
LAB_00586ead:
  *(undefined4 *)(param_1 + 0x1094) = 0;
  return 0;
}
