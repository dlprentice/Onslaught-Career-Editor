/* address: 0x005715b0 */
/* name: CFastVB__Helper_005715b0 */
/* signature: int CFastVB__Helper_005715b0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Helper_005715b0(void)

{
  int *ptr;
  int iVar1;
  uint uVar2;
  int iVar3;
  void *extraout_EAX;
  int extraout_EAX_00;
  int extraout_EAX_01;
  void *in_ECX;
  void *pvVar4;
  void *pvVar5;
  uint uVar6;
  int *piVar7;
  uint unaff_EDI;
  void *in_stack_00000004;
  undefined1 uStack00000008;
  undefined4 in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;
  undefined1 local_3c [4];
  void *local_38;
  int local_34;
  undefined4 local_30;
  undefined1 local_2c [4];
  void *local_28;
  int local_24;
  undefined4 local_20;
  undefined1 local_1c [4];
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  void *local_c;
  undefined1 *puStack_8;
  uint local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d7f28;
  local_c = ExceptionList;
  iVar1 = _uStack00000008 + -6;
  uVar6 = 0;
  ExceptionList = &local_c;
  *(undefined4 *)((int)in_ECX + 0x18) = 0;
  *(undefined1 *)((int)in_ECX + 0x1c) = 1;
  if (iVar1 < 1) {
    iVar1 = 1;
  }
  *(int *)((int)in_ECX + 0x10) = iVar1;
  *(undefined4 *)((int)in_ECX + 0x14) = in_stack_0000000c;
  if (in_ECX != in_stack_00000004) {
    if (*(int *)((int)in_stack_00000004 + 4) != 0) {
      uVar6 = *(int *)((int)in_stack_00000004 + 8) - *(int *)((int)in_stack_00000004 + 4) >> 1;
    }
    uVar2 = CFastVB__CountWordElements((int)in_ECX);
    if (uVar2 < uVar6) {
      uVar6 = CFastVB__CountWordElements((int)in_stack_00000004);
      uVar2 = CFastVB__Helper_00572f80((int)in_ECX);
      if (uVar6 <= uVar2) {
        iVar1 = *(int *)((int)in_stack_00000004 + 4);
        iVar3 = CFastVB__CountWordElements((int)in_ECX);
        pvVar5 = (void *)(iVar1 + iVar3 * 2);
        CFastVB__Helper_005741d0
                  (*(void **)((int)in_stack_00000004 + 4),pvVar5,*(void **)((int)in_ECX + 4));
        CFastVB__Helper_00573140
                  (pvVar5,*(void **)((int)in_stack_00000004 + 8),*(void **)((int)in_ECX + 8));
        iVar1 = CFastVB__CountWordElements((int)in_stack_00000004);
        *(int *)((int)in_ECX + 8) = *(int *)((int)in_ECX + 4) + iVar1 * 2;
        goto LAB_005716ec;
      }
      VFuncSlot_12_00405db0();
      OID__FreeObject_Callback(*(void **)((int)in_ECX + 4));
      iVar1 = CFastVB__CountWordElements((int)in_stack_00000004);
      if (iVar1 < 0) {
        iVar1 = 0;
      }
      CFastVB__Helper_00426fd0(iVar1 * 2);
      *(void **)((int)in_ECX + 4) = extraout_EAX;
      CFastVB__Helper_00573140
                (*(void **)((int)in_stack_00000004 + 4),*(void **)((int)in_stack_00000004 + 8),
                 extraout_EAX);
      *(int *)((int)in_ECX + 0xc) = extraout_EAX_00;
      iVar1 = extraout_EAX_00;
    }
    else {
      CFastVB__Helper_005741d0
                (*(void **)((int)in_stack_00000004 + 4),*(void **)((int)in_stack_00000004 + 8),
                 *(void **)((int)in_ECX + 4));
      VFuncSlot_12_00405db0();
      iVar1 = CFastVB__CountWordElements((int)in_stack_00000004);
      iVar1 = *(int *)((int)in_ECX + 4) + iVar1 * 2;
    }
    *(int *)((int)in_ECX + 8) = iVar1;
  }
LAB_005716ec:
  local_18 = 0;
  local_1c[0] = uStack00000008;
  local_14 = 0;
  local_10 = 0;
  local_3c[0] = uStack00000008;
  local_38 = (void *)0x0;
  local_34 = 0;
  local_30 = 0;
  local_4._0_1_ = 1;
  local_4._1_3_ = 0;
  CFastVB__BuildTriangleAdjacency(in_ECX,(int)local_1c,(uint)local_3c,in_stack_00000010,unaff_EDI);
  local_28 = (void *)0x0;
  local_2c[0] = uStack00000008;
  local_24 = 0;
  local_20 = 0;
  local_4 = CONCAT31(local_4._1_3_,2);
  CFastVB__Helper_005725e0(in_ECX,local_2c,(int)local_1c,(int)local_3c,(void *)0xa,unaff_EDI);
  CFastVB__Helper_005718c0
            (in_ECX,local_2c,in_stack_00000014,(int)local_3c,in_stack_00000018,unaff_EDI);
  pvVar5 = local_28;
  for (uVar6 = 0; (pvVar5 != (void *)0x0 && (uVar6 < (uint)(local_24 - (int)pvVar5 >> 2)));
      uVar6 = uVar6 + 1) {
    pvVar4 = *(void **)((int)pvVar5 + uVar6 * 4);
    if (pvVar4 != (void *)0x0) {
      CFastVB__ReleaseBufferAndResetTriplet_0056f260((int)pvVar4 + 0xc);
      OID__FreeObject_Callback(pvVar4);
      pvVar5 = local_28;
    }
  }
  pvVar4 = local_38;
  for (uVar6 = 0; (pvVar4 != (void *)0x0 && (uVar6 < (uint)(local_34 - (int)pvVar4 >> 2)));
      uVar6 = uVar6 + 1) {
    piVar7 = *(int **)((int)pvVar4 + uVar6 * 4);
    while (ptr = piVar7, ptr != (int *)0x0) {
      if (ptr[3] == uVar6) {
        piVar7 = (int *)ptr[5];
      }
      else {
        piVar7 = (int *)ptr[6];
      }
      iVar1 = *ptr;
      *ptr = iVar1 + -1;
      pvVar4 = local_38;
      pvVar5 = local_28;
      if (iVar1 + -1 == 0) {
        OID__FreeObject_Callback(ptr);
        pvVar4 = local_38;
        pvVar5 = local_28;
      }
    }
  }
  OID__FreeObject_Callback(pvVar5);
  local_28 = (void *)0x0;
  local_24 = 0;
  local_20 = 0;
  local_4 = local_4 & 0xffffff00;
  VFuncSlot_12_00405db0();
  OID__FreeObject_Callback(local_38);
  local_38 = (void *)0x0;
  local_34 = 0;
  local_30 = 0;
  local_4 = 0xffffffff;
  CFastVB__ReleaseBufferAndResetTriplet_0056f260((int)local_1c);
  ExceptionList = local_c;
  return extraout_EAX_01;
}
