/* address: 0x0056eb90 */
/* name: CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer */
/* signature: void __cdecl CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer(void * param_1, uint param_2, void * param_3, void * param_4) */


void __cdecl
CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer
          (void *param_1,uint param_2,void *param_3,void *param_4)

{
  ushort uVar1;
  int iVar2;
  void *ptr;
  undefined1 uVar3;
  bool bVar4;
  int iVar5;
  uint uVar6;
  undefined4 *extraout_EAX;
  int iVar7;
  undefined4 extraout_EAX_00;
  uint *extraout_EAX_01;
  int extraout_EAX_02;
  undefined4 extraout_EAX_03;
  undefined4 extraout_ECX;
  uint uVar8;
  ushort uVar9;
  uint uVar10;
  void *unaff_EDI;
  undefined4 *puVar11;
  int *piVar12;
  undefined4 local_70;
  undefined1 local_6c;
  void *local_68;
  int local_64;
  undefined4 local_60;
  undefined1 local_5c [4];
  void *local_58;
  int local_54;
  undefined4 local_50;
  undefined1 local_4c [4];
  void *local_48;
  int local_44;
  undefined4 local_40;
  undefined1 local_3c [4];
  void *local_38;
  void *local_34;
  undefined4 local_30;
  undefined1 local_2c [32];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  uVar8 = param_2;
  puStack_8 = &LAB_005d7eae;
  local_c = ExceptionList;
  local_3c[0] = param_4._0_1_;
  local_38 = (void *)0x0;
  local_34 = (void *)0x0;
  local_30 = 0;
  local_4 = 0;
  local_70 = 0;
  if (param_2 == 0) {
    ExceptionList = &local_c;
    iVar5 = CFastVB__CountWordElements((int)local_3c);
    if (iVar5 != 0) {
      CFastVB__CopyWordRangeToBufferAndAdvanceEnd(local_3c,(int)local_38,local_34,unaff_EDI);
    }
  }
  else {
    puVar11 = &local_70;
    ExceptionList = &local_c;
    iVar5 = CFastVB__CountWordElements((int)local_3c);
    CFastVB__InsertWordSpanFilled(local_3c,0,(void *)(uVar8 - iVar5),(uint)puVar11,unaff_EDI);
  }
  uVar9 = 0;
  uVar6 = 0;
  if (uVar8 != 0) {
    do {
      *(undefined2 *)((int)local_38 + uVar6 * 2) = *(undefined2 *)((int)param_1 + uVar6 * 2);
      uVar1 = *(ushort *)((int)param_1 + uVar6 * 2);
      if (uVar9 < uVar1) {
        uVar9 = uVar1;
      }
      uVar6 = uVar6 + 1;
    } while (uVar6 < uVar8);
  }
  local_58 = (void *)0x0;
  local_5c[0] = param_4._0_1_;
  local_54 = 0;
  local_50 = 0;
  local_68 = (void *)0x0;
  local_6c = param_4._0_1_;
  local_64 = 0;
  local_60 = 0;
  local_4._0_1_ = 2;
  CFastVB__InitWordSpanHeader(local_2c);
  local_4._0_1_ = 3;
  CFastVB__BuildStripBatchesFromIndexBuffer();
  local_48 = (void *)0x0;
  local_4c[0] = param_4._0_1_;
  local_44 = 0;
  local_40 = 0;
  local_4._0_1_ = 4;
  uVar3 = (undefined1)local_4;
  local_4._0_1_ = 4;
  param_2 = 0;
  if (DAT_009d0c40 == '\0') {
    local_4._0_1_ = uVar3;
    CFastVB__EmitTriangleStripIndexBuffer
              ((int)local_5c,(int)local_4c,CONCAT31((int3)((uint)extraout_ECX >> 8),DAT_00656e60),
               &param_2);
    *(short *)param_4 = (short)param_2;
    if ((local_68 != (void *)0x0) && (local_64 - (int)local_68 >> 2 != 0)) {
      *(short *)param_4 = (short)param_2 + 1;
    }
    uVar8 = (uint)*(ushort *)param_4;
    OID__AllocObject_DefaultTag_00662b2c(uVar8 * 0xc + 4);
    local_4._0_1_ = 6;
    if (extraout_EAX_01 == (uint *)0x0) {
      param_1 = (void *)0x0;
    }
    else {
      param_1 = extraout_EAX_01 + 1;
      *extraout_EAX_01 = uVar8;
      eh_vector_constructor_iterator(param_1,0xc,uVar8,&LAB_0056f4e0,CLandscapeTexture__FreeTexture)
      ;
    }
    local_4 = CONCAT31(local_4._1_3_,4);
    uVar8 = 0;
    *(void **)param_3 = param_1;
    uVar6 = 0;
    if (param_2 != 0) {
      piVar12 = (int *)((int)param_1 + 8);
      do {
        uVar10 = uVar8;
        if (DAT_00656e60 == '\0') {
          for (; ((local_48 != (void *)0x0 && (uVar10 < (uint)(local_44 - (int)local_48 >> 2))) &&
                 (*(int *)((int)local_48 + uVar10 * 4) != -1)); uVar10 = uVar10 + 1) {
          }
          iVar5 = uVar10 - uVar8;
        }
        else if (local_48 == (void *)0x0) {
          iVar5 = 0;
        }
        else {
          iVar5 = local_44 - (int)local_48 >> 2;
        }
        piVar12[-2] = 1;
        OID__AllocObject_DefaultTag_00662b2c(iVar5 * 2);
        piVar12[-1] = iVar5;
        iVar5 = iVar5 + uVar8;
        *piVar12 = extraout_EAX_02;
        if ((int)uVar8 < iVar5) {
          iVar7 = 0;
          do {
            iVar2 = uVar8 * 4;
            uVar8 = uVar8 + 1;
            *(undefined2 *)(iVar7 + *piVar12) = *(undefined2 *)((int)local_48 + iVar2);
            iVar7 = iVar7 + 2;
          } while ((int)uVar8 < iVar5);
        }
        uVar6 = uVar6 + 1;
        piVar12 = piVar12 + 3;
        uVar8 = iVar5 + 1;
      } while (uVar6 < param_2);
    }
    if ((local_68 != (void *)0x0) &&
       (param_3 = (void *)(local_64 - (int)local_68 >> 2), param_3 != (void *)0x0)) {
      puVar11 = (undefined4 *)((int)param_1 + (*(ushort *)param_4 - 1) * 0xc);
      *puVar11 = 0;
      if (local_68 == (void *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = local_64 - (int)local_68 >> 2;
      }
      OID__AllocObject_DefaultTag_00662b2c(iVar5 * 6);
      puVar11[2] = extraout_EAX_03;
      if (local_68 == (void *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = local_64 - (int)local_68 >> 2;
      }
      uVar8 = 0;
      puVar11[1] = iVar5 * 3;
      iVar5 = 0;
      while ((local_68 != (void *)0x0 && (uVar8 < (uint)(local_64 - (int)local_68 >> 2)))) {
        *(undefined2 *)(iVar5 + puVar11[2]) = **(undefined2 **)((int)local_68 + uVar8 * 4);
        iVar7 = uVar8 * 4;
        uVar8 = uVar8 + 1;
        *(undefined2 *)(iVar5 + 2 + puVar11[2]) =
             *(undefined2 *)(*(int *)((int)local_68 + iVar7) + 4);
        *(undefined2 *)(iVar5 + 4 + puVar11[2]) =
             *(undefined2 *)(*(int *)((int)local_68 + uVar8 * 4 + -4) + 8);
        iVar5 = iVar5 + 6;
      }
    }
  }
  else {
    *(undefined2 *)param_4 = 1;
    OID__AllocObject_DefaultTag_00662b2c(0x10);
    local_4._0_1_ = 5;
    if (extraout_EAX == (undefined4 *)0x0) {
      puVar11 = (undefined4 *)0x0;
    }
    else {
      puVar11 = extraout_EAX + 1;
      *extraout_EAX = 1;
      eh_vector_constructor_iterator(puVar11,0xc,1,&LAB_0056f4e0,CLandscapeTexture__FreeTexture);
    }
    local_4 = CONCAT31(local_4._1_3_,4);
    *(undefined4 **)param_3 = puVar11;
    iVar5 = 0;
    uVar8 = 0;
    while ((local_58 != (void *)0x0 && (uVar8 < (uint)(local_54 - (int)local_58 >> 2)))) {
      iVar7 = *(int *)((int)local_58 + uVar8 * 4);
      iVar2 = *(int *)(iVar7 + 0x10);
      if (iVar2 == 0) {
        uVar8 = uVar8 + 1;
      }
      else {
        uVar8 = uVar8 + 1;
        iVar5 = (*(int *)(iVar7 + 0x14) - iVar2 >> 2) * 3 + iVar5;
      }
    }
    if (local_68 == (void *)0x0) {
      iVar7 = 0;
    }
    else {
      iVar7 = local_64 - (int)local_68 >> 2;
    }
    iVar5 = iVar7 * 3 + iVar5;
    *puVar11 = 0;
    puVar11[1] = iVar5;
    OID__AllocObject_DefaultTag_00662b2c(iVar5 * 2);
    iVar5 = 0;
    puVar11[2] = extraout_EAX_00;
    for (param_4 = (void *)0x0;
        (local_58 != (void *)0x0 && (param_4 < (void *)(local_54 - (int)local_58 >> 2)));
        param_4 = (void *)((int)param_4 + 1)) {
      uVar8 = 0;
      while( true ) {
        iVar7 = *(int *)((int)local_58 + (int)param_4 * 4);
        iVar2 = *(int *)(iVar7 + 0x10);
        if ((iVar2 == 0) || ((uint)(*(int *)(iVar7 + 0x14) - iVar2 >> 2) <= uVar8)) break;
        bVar4 = CFastVB__HasDuplicateTriangleIndices32(*(void **)(iVar2 + uVar8 * 4));
        if (bVar4) {
          uVar8 = uVar8 + 1;
          puVar11[1] = puVar11[1] + -3;
        }
        else {
          iVar5 = iVar5 + 3;
          uVar8 = uVar8 + 1;
          *(undefined2 *)(puVar11[2] + -6 + iVar5 * 2) =
               **(undefined2 **)
                 (*(int *)(*(int *)((int)local_58 + (int)param_4 * 4) + 0x10) + -4 + uVar8 * 4);
          *(undefined2 *)(puVar11[2] + -4 + iVar5 * 2) =
               *(undefined2 *)
                (*(int *)(*(int *)(*(int *)((int)local_58 + (int)param_4 * 4) + 0x10) + -4 +
                         uVar8 * 4) + 4);
          *(undefined2 *)(puVar11[2] + -2 + iVar5 * 2) =
               *(undefined2 *)
                (*(int *)(*(int *)(*(int *)((int)local_58 + (int)param_4 * 4) + 0x10) + -4 +
                         uVar8 * 4) + 8);
        }
      }
    }
    uVar8 = 0;
    iVar5 = iVar5 * 2;
    while ((local_68 != (void *)0x0 && (uVar8 < (uint)(local_64 - (int)local_68 >> 2)))) {
      *(undefined2 *)(iVar5 + puVar11[2]) = **(undefined2 **)((int)local_68 + uVar8 * 4);
      iVar7 = uVar8 * 4;
      uVar8 = uVar8 + 1;
      *(undefined2 *)(iVar5 + 2 + puVar11[2]) = *(undefined2 *)(*(int *)((int)local_68 + iVar7) + 4)
      ;
      *(undefined2 *)(iVar5 + 4 + puVar11[2]) =
           *(undefined2 *)(*(int *)((int)local_68 + uVar8 * 4 + -4) + 8);
      iVar5 = iVar5 + 6;
    }
  }
  uVar8 = 0;
  while ((local_58 != (void *)0x0 && (uVar8 < (uint)(local_54 - (int)local_58 >> 2)))) {
    uVar6 = 0;
    while( true ) {
      iVar5 = *(int *)((int)local_58 + uVar8 * 4);
      iVar7 = *(int *)(iVar5 + 0x10);
      if ((iVar7 == 0) || ((uint)(*(int *)(iVar5 + 0x14) - iVar7 >> 2) <= uVar6)) break;
      OID__FreeObject_Callback(*(void **)(iVar7 + uVar6 * 4));
      uVar6 = uVar6 + 1;
      *(undefined4 *)(*(int *)(*(int *)((int)local_58 + uVar8 * 4) + 0x10) + -4 + uVar6 * 4) = 0;
    }
    ptr = *(void **)((int)local_58 + uVar8 * 4);
    if (ptr != (void *)0x0) {
      OID__FreeObject_Callback(*(void **)((int)ptr + 0x10));
      *(undefined4 *)((int)ptr + 0x10) = 0;
      *(undefined4 *)((int)ptr + 0x14) = 0;
      *(undefined4 *)((int)ptr + 0x18) = 0;
      OID__FreeObject_Callback(ptr);
    }
    uVar8 = uVar8 + 1;
    *(undefined4 *)((int)local_58 + uVar8 * 4 + -4) = 0;
  }
  for (uVar8 = 0; (local_68 != (void *)0x0 && (uVar8 < (uint)(local_64 - (int)local_68 >> 2)));
      uVar8 = uVar8 + 1) {
    OID__FreeObject_Callback(*(void **)((int)local_68 + uVar8 * 4));
    *(undefined4 *)((int)local_68 + uVar8 * 4) = 0;
  }
  OID__FreeObject_Callback(local_48);
  local_48 = (void *)0x0;
  local_44 = 0;
  local_40 = 0;
  local_4 = CONCAT31(local_4._1_3_,2);
  CFastVB__ReleaseBufferAndResetTriplet_0056f520((int)local_2c);
  OID__FreeObject_Callback(local_68);
  local_68 = (void *)0x0;
  local_64 = 0;
  local_60 = 0;
  OID__FreeObject_Callback(local_58);
  local_58 = (void *)0x0;
  local_54 = 0;
  local_50 = 0;
  OID__FreeObject_Callback(local_38);
  ExceptionList = local_c;
  return;
}
