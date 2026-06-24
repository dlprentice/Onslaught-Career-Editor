/* address: 0x0059a21f */
/* name: CFastVB__AreNodeTreesCompatible */
/* signature: int __stdcall CFastVB__AreNodeTreesCompatible(void * param_1, void * param_2, int param_3) */


int CFastVB__AreNodeTreesCompatible(void *param_1,void *param_2,int param_3)

{
  int iVar1;
  uint uVar2;
  undefined3 extraout_var;
  uint uVar3;
  undefined1 *puVar4;
  int iVar5;
  int unaff_EDI;
  undefined1 *puVar6;
  bool bVar7;
  undefined1 local_50 [16];
  undefined4 local_40;
  undefined4 local_38;
  int local_34;
  undefined1 local_2c [16];
  undefined4 local_1c;
  undefined4 local_14;
  int local_10;
  void *local_8;

  if (param_3 == 0) {
    if (param_1 == (void *)0x0) {
      if (param_2 != (void *)0x0) {
        return 0;
      }
      return 1;
    }
  }
  else if (param_1 == (void *)0x0) {
    return 1;
  }
  if (param_2 == (void *)0x0) {
    return 0;
  }
  CFastVB__InitNodeType9(local_50);
  CFastVB__InitNodeType9(local_2c);
  puVar6 = param_1;
  if (*(int *)((int)param_1 + 4) != 8) {
    local_40 = 4;
    local_38 = 1;
    local_34 = CFastVB__Helper_00599c49(local_8,(int)param_1,unaff_EDI);
    puVar6 = local_50;
    if ((param_3 != 0) &&
       (iVar5 = CFastVB__Helper_00599bd7(local_8,(int)param_1,unaff_EDI), iVar5 != 0)) {
      local_40 = 1;
    }
  }
  puVar4 = param_2;
  if (*(int *)((int)param_2 + 4) != 8) {
    local_1c = 4;
    local_14 = 1;
    local_10 = CFastVB__Helper_00599c49(local_8,(int)param_2,unaff_EDI);
    puVar4 = local_2c;
    if ((param_3 != 0) &&
       (iVar5 = CFastVB__Helper_00599bd7(local_8,(int)param_2,unaff_EDI), iVar5 != 0)) {
      local_1c = 1;
    }
  }
  iVar5 = *(int *)(puVar6 + 0x10);
  if ((iVar5 != 4) && (iVar1 = *(int *)(puVar4 + 0x10), iVar1 != 4)) {
    if (iVar5 == 0) {
joined_r0x0059a3ec:
      if (iVar1 == 3) goto LAB_0059a497;
    }
    else if (iVar5 == 1) {
      if (iVar1 != 0) {
        if (iVar1 == 1) {
LAB_0059a3d8:
          if (*(uint *)(puVar6 + 0x1c) <= *(uint *)(puVar4 + 0x1c)) goto LAB_0059a30f;
        }
        else {
          if (iVar1 != 2) goto joined_r0x0059a3ec;
          uVar2 = *(uint *)(puVar4 + 0x18);
          if (((uVar2 != 1) || (*(uint *)(puVar6 + 0x1c) <= *(uint *)(puVar4 + 0x1c))) &&
             ((iVar5 = *(int *)(puVar4 + 0x1c), iVar5 != 1 || (*(uint *)(puVar6 + 0x1c) <= uVar2))))
          {
            if ((uVar2 != 1) && (iVar5 != 1)) {
              bVar7 = uVar2 * iVar5 - *(int *)(puVar6 + 0x1c) == 0;
              goto LAB_0059a477;
            }
            goto LAB_0059a30f;
          }
        }
        goto LAB_0059a497;
      }
    }
    else if (iVar5 == 2) {
      if (iVar1 != 0) {
        if (iVar1 == 1) {
          uVar2 = *(uint *)(puVar6 + 0x18);
          if (((uVar2 != 1) || (*(uint *)(puVar6 + 0x1c) <= *(uint *)(puVar4 + 0x1c))) &&
             ((iVar5 = *(int *)(puVar6 + 0x1c), iVar5 != 1 || (uVar2 <= *(uint *)(puVar4 + 0x1c)))))
          {
            if ((uVar2 != 1) && (iVar5 != 1)) {
              bVar7 = uVar2 * iVar5 - *(int *)(puVar4 + 0x1c) == 0;
              goto LAB_0059a477;
            }
            goto LAB_0059a30f;
          }
        }
        else {
          if (iVar1 != 2) goto joined_r0x0059a3ec;
          if (*(uint *)(puVar6 + 0x18) <= *(uint *)(puVar4 + 0x18)) goto LAB_0059a3d8;
        }
        goto LAB_0059a497;
      }
    }
    else if (iVar5 == 3) {
      if (iVar1 != 3) goto LAB_0059a497;
      iVar5 = *(int *)(puVar4 + 0x14);
      if (iVar5 != 0xd) {
        if (iVar5 == 0xf) {
          iVar5 = *(int *)(puVar6 + 0x14);
          if (((iVar5 == 0xf) || (iVar5 == 0x10)) || ((iVar5 == 0x11 || (iVar5 == 0x12))))
          goto LAB_0059a30f;
          bVar7 = iVar5 == 0x13;
        }
        else if (iVar5 == 0x14) {
          iVar5 = *(int *)(puVar6 + 0x14);
          if ((((iVar5 == 0x14) || (iVar5 == 0x15)) || (iVar5 == 0x16)) || (iVar5 == 0x17))
          goto LAB_0059a30f;
          bVar7 = iVar5 == 0x18;
        }
        else {
          bVar7 = *(int *)(puVar6 + 0x14) == iVar5;
        }
LAB_0059a477:
        if (!bVar7) goto LAB_0059a497;
      }
    }
LAB_0059a30f:
    iVar5 = 1;
    goto LAB_0059a311;
  }
  uVar3 = *(int *)(puVar6 + 0x1c) * *(int *)(puVar6 + 0x18);
  uVar2 = *(int *)(puVar4 + 0x1c) * *(int *)(puVar4 + 0x18);
  if (param_3 == 0) {
    if ((iVar5 == *(int *)(puVar4 + 0x10)) && (uVar3 - uVar2 == 0)) {
      uVar2 = 0;
      if (uVar3 != 0) {
        do {
          iVar5 = CFastVB__Helper_00599d80(local_8,param_1,uVar2,(uint)local_50,unaff_EDI);
          if (((iVar5 < 0) ||
              (iVar5 = CFastVB__Helper_00599d80(local_8,param_2,uVar2,(uint)local_2c,unaff_EDI),
              iVar5 < 0)) ||
             (bVar7 = CFastVB__Helper_00599cd2((int)local_50,(int)local_2c),
             CONCAT31(extraout_var,bVar7) == 0)) goto LAB_0059a497;
          uVar2 = uVar2 + 1;
        } while (uVar2 < uVar3);
      }
      goto LAB_0059a545;
    }
  }
  else if (uVar3 < uVar2 || uVar3 - uVar2 == 0) {
    uVar2 = 0;
    if (uVar3 != 0) {
      do {
        iVar5 = CFastVB__Helper_00599d80(local_8,param_1,uVar2,(uint)local_50,unaff_EDI);
        if (((iVar5 < 0) ||
            (iVar5 = CFastVB__Helper_00599d80(local_8,param_2,uVar2,(uint)local_2c,unaff_EDI),
            iVar5 < 0)) ||
           (iVar5 = CFastVB__AreNodeTreesCompatible(local_50,local_2c,1), iVar5 == 0))
        goto LAB_0059a497;
        uVar2 = uVar2 + 1;
      } while (uVar2 < uVar3);
    }
LAB_0059a545:
    iVar5 = 1;
    goto LAB_0059a311;
  }
LAB_0059a497:
  iVar5 = 0;
LAB_0059a311:
  CFastVB__Helper_00598abd(local_2c);
  CFastVB__Helper_00598abd(local_50);
  return iVar5;
}
