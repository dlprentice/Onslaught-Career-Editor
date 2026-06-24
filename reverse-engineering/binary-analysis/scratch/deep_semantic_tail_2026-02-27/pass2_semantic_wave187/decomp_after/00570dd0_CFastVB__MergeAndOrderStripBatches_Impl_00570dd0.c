/* address: 0x00570dd0 */
/* name: CFastVB__MergeAndOrderStripBatches_Impl_00570dd0 */
/* signature: void __thiscall CFastVB__MergeAndOrderStripBatches_Impl_00570dd0(void * this, int param_1, int param_2, int param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__MergeAndOrderStripBatches_Impl_00570dd0
          (void *this,int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 *ptr;
  int *extraout_EAX;
  int extraout_EAX_00;
  int iVar3;
  void *pvVar4;
  int iVar5;
  int *ptr_00;
  void *unaff_ESI;
  void *unaff_EDI;
  uint uVar6;
  undefined4 *puVar7;
  undefined1 local_1c [4];
  void *local_18;
  int local_14;
  undefined4 local_10;
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d7f03;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CFastVB__AppendDwordRangeToSpanBuilder_00572f20
            ((void *)param_3,*(int *)(param_3 + 4),*(void **)(param_3 + 8),unaff_EDI);
  CFastVB__AppendDwordRangeToSpanBuilder_00572f20
            ((void *)param_2,*(int *)(param_2 + 4),*(void **)(param_2 + 8),unaff_EDI);
  local_1c[0] = (undefined1)param_3;
  local_18 = (void *)0x0;
  local_14 = 0;
  local_10 = 0;
  local_4 = 0;
  uVar6 = 0;
  do {
    while( true ) {
      iVar5 = *(int *)(param_1 + 4);
      if ((iVar5 == 0) || ((uint)(*(int *)(param_1 + 8) - iVar5 >> 2) <= uVar6)) {
        iVar5 = 0;
        if (local_18 != (void *)0x0) {
          iVar5 = local_14 - (int)local_18 >> 2;
        }
        OID__AllocObject_DefaultTag_00662b2c(iVar5);
        if (local_18 == (void *)0x0) {
          uVar6 = 0;
        }
        else {
          uVar6 = local_14 - (int)local_18 >> 2;
        }
        puVar7 = ptr;
        for (uVar2 = uVar6 >> 2; uVar2 != 0; uVar2 = uVar2 - 1) {
          *puVar7 = 0;
          puVar7 = puVar7 + 1;
        }
        for (uVar6 = uVar6 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
          *(undefined1 *)puVar7 = 0;
          puVar7 = (undefined4 *)((int)puVar7 + 1);
        }
        OID__AllocObject_DefaultTag_00662b2c(8);
        local_4._0_1_ = 1;
        if (extraout_EAX == (int *)0x0) {
          ptr_00 = (int *)0x0;
        }
        else {
          iVar5 = *(int *)((int)this + 0x10);
          extraout_EAX[1] = iVar5;
          OID__AllocObject_DefaultTag_00662b2c(iVar5 * 4);
          *extraout_EAX = extraout_EAX_00;
          iVar5 = 0;
          ptr_00 = extraout_EAX;
          if (0 < extraout_EAX[1]) {
            do {
              iVar5 = iVar5 + 1;
              *(undefined4 *)(*extraout_EAX + -4 + iVar5 * 4) = 0xffffffff;
            } while (iVar5 < extraout_EAX[1]);
          }
        }
        local_4 = (uint)local_4._1_3_ << 8;
        uVar6 = param_3;
        while( true ) {
          iVar5 = -1;
          pvVar4 = local_18;
          for (uVar2 = 0; (pvVar4 != (void *)0x0 && (uVar2 < (uint)(local_14 - (int)pvVar4 >> 2)));
              uVar2 = uVar2 + 1) {
            if ((*(char *)(uVar2 + (int)ptr) == '\0') &&
               (iVar3 = CFastVB__CountTriangleVerticesInSet_00572490
                                  (ptr_00,*(void **)((int)pvVar4 + uVar2 * 4)), pvVar4 = local_18,
               iVar5 < iVar3)) {
              uVar6 = uVar2;
              iVar5 = iVar3;
            }
          }
          if ((float)iVar5 == _DAT_005e6a38) break;
          *(undefined1 *)((int)ptr + uVar6) = 1;
          CDXTexture__InsertUniqueTripletAtFront(ptr_00,*(void **)((int)local_18 + uVar6 * 4));
          CFastVB__InsertDwordSpanFilled
                    ((void *)param_3,*(int *)(param_3 + 8),(void *)0x1,
                     (uint)((int)local_18 + uVar6 * 4),unaff_ESI);
        }
        if (ptr_00 != (int *)0x0) {
          OID__FreeObject_Callback((void *)*ptr_00);
          *ptr_00 = 0;
          OID__FreeObject_Callback(ptr_00);
        }
        OID__FreeObject_Callback(ptr);
        OID__FreeObject_Callback(local_18);
        ExceptionList = local_c;
        return;
      }
      iVar3 = *(int *)(iVar5 + uVar6 * 4);
      iVar1 = *(int *)(iVar3 + 0x10);
      if (iVar1 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = *(int *)(iVar3 + 0x14) - iVar1 >> 2;
      }
      if (uVar2 < *(uint *)((int)this + 0x14)) break;
      CFastVB__InsertDwordSpanFilled
                ((void *)param_2,*(int *)(param_2 + 8),(void *)0x1,iVar5 + uVar6 * 4,unaff_ESI);
LAB_00570edb:
      uVar6 = uVar6 + 1;
    }
    uVar2 = 0;
    while( true ) {
      iVar5 = *(int *)(*(int *)(param_1 + 4) + uVar6 * 4);
      iVar3 = *(int *)(iVar5 + 0x10);
      if ((iVar3 == 0) || ((uint)(*(int *)(iVar5 + 0x14) - iVar3 >> 2) <= uVar2)) break;
      CFastVB__InsertDwordAndGrow(local_1c,local_14,(void *)(iVar3 + uVar2 * 4),unaff_ESI);
      uVar2 = uVar2 + 1;
    }
    pvVar4 = *(void **)(*(int *)(param_1 + 4) + uVar6 * 4);
    if (pvVar4 == (void *)0x0) goto LAB_00570edb;
    CFastVB__ReleaseBufferAndResetTriplet_0056f260((int)pvVar4 + 0xc);
    OID__FreeObject_Callback(pvVar4);
    uVar6 = uVar6 + 1;
  } while( true );
}
