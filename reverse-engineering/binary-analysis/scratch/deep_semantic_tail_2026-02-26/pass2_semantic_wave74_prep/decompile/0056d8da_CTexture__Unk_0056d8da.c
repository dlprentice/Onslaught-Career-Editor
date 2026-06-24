/* address: 0x0056d8da */
/* name: CTexture__Unk_0056d8da */
/* signature: void __cdecl CTexture__Unk_0056d8da(void * param_1, void * param_2) */


void __cdecl CTexture__Unk_0056d8da(void *param_1,void *param_2)

{
  void *pvVar1;
  short sVar2;
  int iVar3;
  void *pvVar4;
  void *pvVar5;
  ushort uVar6;
  uint uVar7;
  int iVar8;
  ushort uVar9;
  uint uVar10;
  ushort uVar11;
  byte local_28;
  undefined1 uStack_27;
  undefined2 uStack_26;
  short local_24;
  undefined2 uStack_22;
  undefined2 local_20;
  undefined1 uStack_1e;
  byte bStack_1d;
  void *local_1c;
  int local_18;
  int local_14;
  ushort *local_10;
  ushort *local_c;
  short *local_8;

  pvVar5 = param_2;
  pvVar4 = param_1;
  local_18 = 0;
  local_28 = 0;
  uStack_27 = 0;
  uStack_26 = 0;
  local_24 = 0;
  uStack_22 = 0;
  local_20 = 0;
  uStack_1e = 0;
  bStack_1d = 0;
  uVar7 = *(ushort *)((int)param_1 + 10) & 0x7fff;
  uVar10 = *(ushort *)((int)param_2 + 10) & 0x7fff;
  uVar11 = (*(ushort *)((int)param_2 + 10) ^ *(ushort *)((int)param_1 + 10)) & 0x8000;
  uVar6 = (ushort)uVar7;
  pvVar1 = (void *)(uVar10 + uVar7);
  if (((uVar6 < 0x7fff) && (uVar9 = (ushort)uVar10, uVar9 < 0x7fff)) && ((ushort)pvVar1 < 0xbffe)) {
    if ((ushort)pvVar1 < 0x3fc0) {
LAB_0056d97d:
      *(undefined4 *)((int)pvVar4 + 8) = 0;
      *(undefined4 *)((int)pvVar4 + 4) = 0;
      *(undefined4 *)pvVar4 = 0;
      return;
    }
    if (((uVar6 != 0) ||
        (pvVar1 = (void *)((int)pvVar1 + 1), (*(uint *)((int)param_1 + 8) & 0x7fffffff) != 0)) ||
       ((uVar6 = 0, *(int *)((int)param_1 + 4) != 0 || (*(int *)param_1 != 0)))) {
      param_1 = pvVar1;
      if (((uVar9 == 0) &&
          (param_1 = (void *)((int)param_1 + 1), (*(uint *)((int)param_2 + 8) & 0x7fffffff) == 0))
         && ((*(int *)((int)param_2 + 4) == 0 && (*(int *)param_2 == 0)))) goto LAB_0056d97d;
      local_14 = 0;
      local_8 = &local_24;
      param_2 = (void *)0x5;
      do {
        if (0 < (int)param_2) {
          local_c = (ushort *)(local_14 * 2 + (int)pvVar4);
          local_10 = (ushort *)((int)pvVar5 + 8);
          local_1c = param_2;
          do {
            iVar8 = CDXTexture__Helper_0056d4a6
                              (*(uint *)(local_8 + -2),(uint)*local_c * (uint)*local_10,local_8 + -2
                              );
            if (iVar8 != 0) {
              *local_8 = *local_8 + 1;
            }
            local_c = local_c + 1;
            local_10 = local_10 + -1;
            local_1c = (void *)((int)local_1c + -1);
          } while (local_1c != (void *)0x0);
        }
        local_8 = local_8 + 1;
        local_14 = local_14 + 1;
        param_2 = (void *)((int)param_2 + -1);
      } while (0 < (int)param_2);
      param_1 = (void *)((int)param_1 + 0xc002);
      if ((short)(ushort)param_1 < 1) {
LAB_0056da31:
        param_1._0_2_ = (ushort)param_1 - 1;
        if ((short)(ushort)param_1 < 0) {
          iVar8 = -(int)(short)(ushort)param_1;
          param_1._0_2_ = (ushort)param_1 + (short)iVar8;
          do {
            if ((local_28 & 1) != 0) {
              local_18 = local_18 + 1;
            }
            CTexture__Helper_0056d553(&local_28);
            iVar8 = iVar8 + -1;
          } while (iVar8 != 0);
          if (local_18 != 0) {
            local_28 = local_28 | 1;
          }
        }
      }
      else {
        do {
          if ((bStack_1d & 0x80) != 0) break;
          CTexture__Helper_0056d525(&local_28);
          param_1 = (void *)((int)param_1 + 0xffff);
        } while (0 < (short)(ushort)param_1);
        if ((short)(ushort)param_1 < 1) goto LAB_0056da31;
      }
      if ((0x8000 < CONCAT11(uStack_27,local_28)) ||
         (sVar2 = CONCAT11(bStack_1d,uStack_1e), iVar3 = CONCAT22(local_20,uStack_22),
         iVar8 = CONCAT22(local_24,uStack_26),
         (CONCAT22(uStack_26,CONCAT11(uStack_27,local_28)) & 0x1ffff) == 0x18000)) {
        if (CONCAT22(local_24,uStack_26) == -1) {
          iVar8 = 0;
          if (CONCAT22(local_20,uStack_22) == -1) {
            if (CONCAT11(bStack_1d,uStack_1e) == -1) {
              param_1._0_2_ = (ushort)param_1 + 1;
              sVar2 = -0x8000;
              iVar3 = 0;
              iVar8 = 0;
            }
            else {
              sVar2 = CONCAT11(bStack_1d,uStack_1e) + 1;
              iVar3 = 0;
              iVar8 = 0;
            }
          }
          else {
            sVar2 = CONCAT11(bStack_1d,uStack_1e);
            iVar3 = CONCAT22(local_20,uStack_22) + 1;
          }
        }
        else {
          iVar8 = CONCAT22(local_24,uStack_26) + 1;
          sVar2 = CONCAT11(bStack_1d,uStack_1e);
          iVar3 = CONCAT22(local_20,uStack_22);
        }
      }
      local_24 = (short)((uint)iVar8 >> 0x10);
      uStack_26 = (undefined2)iVar8;
      local_20 = (undefined2)((uint)iVar3 >> 0x10);
      uStack_22 = (undefined2)iVar3;
      bStack_1d = (byte)((ushort)sVar2 >> 8);
      uStack_1e = (undefined1)sVar2;
      if (0x7ffe < (ushort)param_1) goto LAB_0056dada;
      uVar6 = (ushort)param_1 | uVar11;
      *(undefined2 *)pvVar4 = uStack_26;
      *(uint *)((int)pvVar4 + 2) = CONCAT22(uStack_22,local_24);
      *(uint *)((int)pvVar4 + 6) = CONCAT13(bStack_1d,CONCAT12(uStack_1e,local_20));
    }
    *(ushort *)((int)pvVar4 + 10) = uVar6;
  }
  else {
LAB_0056dada:
    *(undefined4 *)((int)pvVar4 + 4) = 0;
    *(undefined4 *)pvVar4 = 0;
    *(uint *)((int)pvVar4 + 8) = (-(uint)(uVar11 != 0) & 0x80000000) + 0x7fff8000;
  }
  return;
}
