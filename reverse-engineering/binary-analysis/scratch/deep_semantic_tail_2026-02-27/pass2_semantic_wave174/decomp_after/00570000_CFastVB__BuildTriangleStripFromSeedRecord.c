/* address: 0x00570000 */
/* name: CFastVB__BuildTriangleStripFromSeedRecord */
/* signature: void __thiscall CFastVB__BuildTriangleStripFromSeedRecord(void * this, void * param_1, int param_2) */


void __thiscall CFastVB__BuildTriangleStripFromSeedRecord(void *this,void *param_1,int param_2)

{
  int *piVar1;
  uint *puVar2;
  uint *puVar3;
  int iVar4;
  uint *extraout_EAX;
  uint *extraout_EAX_00;
  uint uVar5;
  uint *puVar6;
  uint *puVar7;
  uint *puVar8;
  int iVar9;
  uint uVar10;
  uint *puVar11;
  void *unaff_EDI;
  uint *local_6c;
  int *local_68;
  uint *local_64;
  uint *local_60;
  uint *local_5c;
  uint *local_58;
  uint *local_54;
  uint *local_50;
  undefined1 local_4c [4];
  int local_48;
  void *local_44;
  undefined4 local_40;
  undefined1 local_3c [4];
  int local_38;
  int local_34;
  undefined4 local_30;
  undefined1 local_2c [4];
  undefined4 local_28;
  int local_24;
  undefined4 local_20;
  undefined1 local_1c [4];
  undefined4 local_18;
  int local_14;
  undefined4 local_10;
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d7ee0;
  local_c = ExceptionList;
  iVar9 = 0;
  local_4c[0] = param_1._0_1_;
  local_48 = 0;
  local_44 = (void *)0x0;
  local_40 = 0;
  local_3c[0] = param_1._0_1_;
  local_38 = 0;
  local_34 = 0;
  local_30 = 0;
  local_18 = 0;
  local_1c[0] = param_1._0_1_;
  local_14 = 0;
  local_10 = 0;
  local_4 = 2;
  ExceptionList = &local_c;
  local_68 = this;
  CFastVB__Helper_00573170(local_3c,0,this,unaff_EDI);
  iVar4 = *(int *)this;
  if (*(int *)((int)this + 0x20) < 0) {
    *(undefined4 *)(iVar4 + 0x14) = 0xffffffff;
    *(undefined4 *)(iVar4 + 0xc) = *(undefined4 *)((int)this + 0x1c);
  }
  else {
    *(int *)(iVar4 + 0x14) = *(int *)((int)this + 0x20);
    *(undefined4 *)(iVar4 + 0x10) = *(undefined4 *)((int)this + 0x1c);
  }
  iVar4 = *(int *)((int)this + 4);
  if (*(char *)((int)this + 8) == '\0') {
    local_58 = *(uint **)(iVar4 + 0x10);
    puVar3 = *(uint **)(iVar4 + 0xc);
  }
  else {
    local_58 = *(uint **)(iVar4 + 0xc);
    puVar3 = *(uint **)(iVar4 + 0x10);
  }
  local_5c = puVar3;
  local_54 = local_58;
  CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_58,unaff_EDI);
  local_58 = puVar3;
  CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_58,unaff_EDI);
  piVar1 = *(int **)this;
  if (local_48 != 0) {
    iVar9 = (int)local_44 - local_48 >> 1;
  }
  puVar3 = (uint *)piVar1[2];
  uVar10 = (uint)*(ushort *)(local_48 + -4 + iVar9 * 2);
  uVar5 = (uint)*(ushort *)(local_48 + -2 + iVar9 * 2);
  puVar2 = (uint *)*piVar1;
  puVar11 = (uint *)piVar1[1];
  local_64 = puVar2;
  if ((puVar2 == (uint *)uVar10) || (puVar2 == (uint *)uVar5)) {
    if ((puVar11 == (uint *)uVar10) || (puVar11 == (uint *)uVar5)) {
      if ((puVar3 == (uint *)uVar10) || (puVar3 == (uint *)uVar5)) {
        if (((puVar2 != puVar11) && (puVar2 != puVar3)) && (local_64 = puVar11, puVar11 != puVar3))
        {
          local_64 = (uint *)0xffffffff;
        }
      }
      else {
        local_64 = puVar3;
        if (((puVar2 != (uint *)uVar10) && (puVar2 != (uint *)uVar5)) ||
           ((puVar11 != (uint *)uVar10 && (puVar11 != (uint *)uVar5)))) {
          CFastVB__DispatchLockedRoute_6533e0(0x656eec);
          CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
        }
      }
    }
    else if (((puVar2 != (uint *)uVar10) && (puVar2 != (uint *)uVar5)) ||
            ((local_64 = puVar11, puVar3 != (uint *)uVar10 && (puVar3 != (uint *)uVar5)))) {
      CFastVB__DispatchLockedRoute_6533e0(0x656eec);
      CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
      local_64 = puVar11;
    }
  }
  else if (((puVar11 != (uint *)uVar10) && (puVar11 != (uint *)uVar5)) ||
          ((puVar3 != (uint *)uVar10 && (puVar3 != (uint *)uVar5)))) {
    CFastVB__DispatchLockedRoute_6533e0(0x656eec);
    CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
  }
  puVar2 = local_64;
  local_58 = local_64;
  CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_58,unaff_EDI);
  puVar11 = local_5c;
  piVar1 = local_68;
  local_60 = local_5c;
  puVar3 = (uint *)CFastVB__ResolveOppositeAdjacencyRecord
                             ((int)param_1,(int)local_5c,(int)puVar2,*local_68);
  while (((local_6c = puVar3, puVar3 != (uint *)0x0 && ((int)puVar3[3] < 0)) &&
         ((piVar1[8] < 0 || (puVar3[5] != piVar1[8]))))) {
    local_50 = puVar2;
    iVar4 = CFastVB__CountWordElements((int)local_4c);
    puVar11 = (uint *)puVar3[1];
    puVar6 = (uint *)(uint)*(ushort *)(local_48 + -4 + iVar4 * 2);
    puVar8 = (uint *)(uint)*(ushort *)(local_48 + -2 + iVar4 * 2);
    puVar7 = (uint *)*puVar3;
    puVar3 = (uint *)puVar3[2];
    if ((puVar7 == puVar6) || (puVar7 == puVar8)) {
      if ((puVar11 == puVar6) || (puVar11 == puVar8)) {
        if ((puVar3 == puVar6) || (puVar3 == puVar8)) {
          if ((puVar7 != puVar11) && ((puVar7 != puVar3 && (puVar7 = puVar11, puVar11 != puVar3))))
          {
            puVar7 = (uint *)0xffffffff;
          }
        }
        else if (((puVar7 != puVar6) && (puVar7 != puVar8)) ||
                ((puVar7 = puVar3, puVar11 != puVar6 && (puVar11 != puVar8)))) {
          CFastVB__DispatchLockedRoute_6533e0(0x656eec);
          CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
          puVar7 = puVar3;
        }
      }
      else if (((puVar7 != puVar6) && (puVar7 != puVar8)) ||
              ((puVar7 = puVar11, puVar3 != puVar6 && (puVar3 != puVar8)))) {
        CFastVB__DispatchLockedRoute_6533e0(0x656eec);
        CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
        puVar7 = puVar11;
      }
    }
    else if (((puVar11 != puVar6) && (puVar11 != puVar8)) ||
            ((puVar3 != puVar6 && (puVar3 != puVar8)))) {
      CFastVB__DispatchLockedRoute_6533e0(0x656eec);
      CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
    }
    puVar3 = local_6c;
    iVar4 = CFastVB__ResolveOppositeAdjacencyRecord
                      ((int)param_1,(int)puVar2,(int)puVar7,(int)local_6c);
    puVar11 = local_60;
    piVar1 = local_68;
    if ((((iVar4 == 0) || (-1 < *(int *)(iVar4 + 0xc))) ||
        ((puVar6 = local_50, -1 < local_68[8] && (*(int *)(iVar4 + 0x14) == local_68[8])))) &&
       (((iVar4 = CFastVB__ResolveOppositeAdjacencyRecord
                            ((int)param_1,(int)local_60,(int)puVar7,(int)puVar3), puVar6 = local_50,
         iVar4 != 0 && (*(int *)(iVar4 + 0xc) < 0)) &&
        ((piVar1[8] < 0 || (*(int *)(iVar4 + 0x14) != piVar1[8])))))) {
      CFastVB__Helper_00426fd0(0x18);
      if (extraout_EAX == (uint *)0x0) {
        local_58 = (uint *)0x0;
      }
      else {
        extraout_EAX[1] = (uint)puVar2;
        *extraout_EAX = (uint)puVar11;
        extraout_EAX[2] = (uint)puVar11;
        extraout_EAX[3] = 0xffffffff;
        extraout_EAX[4] = 0xffffffff;
        extraout_EAX[5] = 0xffffffff;
        local_58 = extraout_EAX;
      }
      CFastVB__Helper_00573170(local_3c,local_34,&local_58,unaff_EDI);
      if (piVar1[8] < 0) {
        local_58[5] = 0xffffffff;
        local_58[3] = piVar1[7];
      }
      else {
        local_58[5] = piVar1[8];
        local_58[4] = piVar1[7];
      }
      local_60 = puVar11;
      CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_60,unaff_EDI);
      piVar1[10] = piVar1[10] + 1;
      puVar6 = puVar11;
    }
    CFastVB__Helper_00573170(local_3c,local_34,&local_6c,unaff_EDI);
    if (piVar1[8] < 0) {
      local_6c[5] = 0xffffffff;
      local_6c[3] = piVar1[7];
    }
    else {
      local_6c[5] = piVar1[8];
      local_6c[4] = piVar1[7];
    }
    local_50 = puVar7;
    CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_50,unaff_EDI);
    local_60 = puVar6;
    puVar3 = (uint *)CFastVB__ResolveOppositeAdjacencyRecord
                               ((int)param_1,(int)puVar6,(int)puVar7,(int)local_6c);
    piVar1 = local_68;
    puVar2 = puVar7;
    puVar11 = local_5c;
  }
  local_2c[0] = param_1._0_1_;
  local_28 = 0;
  local_24 = 0;
  local_20 = 0;
  local_4._1_3_ = (uint3)((uint)local_4 >> 8);
  local_4 = CONCAT31(local_4._1_3_,3);
  for (uVar10 = 0; (local_38 != 0 && (uVar10 < (uint)(local_34 - local_38 >> 2)));
      uVar10 = uVar10 + 1) {
    CFastVB__Helper_00573170(local_2c,local_24,(void *)(local_38 + uVar10 * 4),unaff_EDI);
  }
  local_50 = (uint *)0x0;
  CFastVB__CountWordElements((int)local_4c);
  iVar4 = CFastVB__CountWordElements((int)local_4c);
  if (iVar4 != 0) {
    CFastVB__CopyWordRangeToBufferAndAdvanceEnd(local_4c,local_48,local_44,unaff_EDI);
  }
  local_50 = local_64;
  CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_50,unaff_EDI);
  local_50 = puVar11;
  CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_50,unaff_EDI);
  puVar3 = local_54;
  local_50 = local_54;
  CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_50,unaff_EDI);
  local_5c = puVar3;
  local_60 = puVar11;
  puVar3 = (uint *)CFastVB__ResolveOppositeAdjacencyRecord
                             ((int)param_1,(int)puVar11,(int)puVar3,*piVar1);
  while ((((local_6c = puVar3, puVar3 != (uint *)0x0 && ((int)puVar3[3] < 0)) &&
          ((piVar1[8] < 0 || (puVar3[5] != piVar1[8])))) &&
         (iVar4 = CTexture__Helper_0056ff40((int)local_2c,puVar3), (char)iVar4 != '\0'))) {
    local_58 = local_5c;
    iVar4 = CFastVB__CountWordElements((int)local_4c);
    puVar2 = (uint *)puVar3[1];
    puVar7 = (uint *)(uint)*(ushort *)(local_48 + -4 + iVar4 * 2);
    puVar6 = (uint *)(uint)*(ushort *)(local_48 + -2 + iVar4 * 2);
    puVar11 = (uint *)*puVar3;
    puVar3 = (uint *)puVar3[2];
    if ((puVar11 == puVar7) || (puVar11 == puVar6)) {
      if ((puVar2 == puVar7) || (puVar2 == puVar6)) {
        if ((puVar3 == puVar7) || (puVar3 == puVar6)) {
          if ((puVar11 != puVar2) && ((puVar11 != puVar3 && (puVar11 = puVar2, puVar2 != puVar3))))
          {
            puVar11 = (uint *)0xffffffff;
          }
        }
        else if (((puVar11 != puVar7) && (puVar11 != puVar6)) ||
                ((puVar11 = puVar3, puVar2 != puVar7 && (puVar2 != puVar6)))) {
          CFastVB__DispatchLockedRoute_6533e0(0x656eec);
          CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
          puVar11 = puVar3;
        }
      }
      else if (((puVar11 != puVar7) && (puVar11 != puVar6)) ||
              ((puVar11 = puVar2, puVar3 != puVar7 && (puVar3 != puVar6)))) {
        CFastVB__DispatchLockedRoute_6533e0(0x656eec);
        CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
        puVar11 = puVar2;
      }
    }
    else if (((puVar2 != puVar7) && (puVar2 != puVar6)) ||
            ((puVar3 != puVar7 && (puVar3 != puVar6)))) {
      CFastVB__DispatchLockedRoute_6533e0(0x656eec);
      CFastVB__DispatchLockedRoute_6533e0(0x656eb0);
    }
    puVar3 = local_6c;
    iVar4 = CFastVB__ResolveOppositeAdjacencyRecord
                      ((int)param_1,(int)local_5c,(int)puVar11,(int)local_6c);
    piVar1 = local_68;
    if ((((iVar4 == 0) || (-1 < *(int *)(iVar4 + 0xc))) ||
        ((-1 < local_68[8] && (*(int *)(iVar4 + 0x14) == local_68[8])))) &&
       (((iVar4 = CFastVB__ResolveOppositeAdjacencyRecord
                            ((int)param_1,(int)local_60,(int)puVar11,(int)puVar3), iVar4 != 0 &&
         (*(int *)(iVar4 + 0xc) < 0)) && ((piVar1[8] < 0 || (*(int *)(iVar4 + 0x14) != piVar1[8]))))
       )) {
      CFastVB__Helper_00426fd0(0x18);
      puVar3 = local_60;
      if (extraout_EAX_00 == (uint *)0x0) {
        local_54 = (uint *)0x0;
      }
      else {
        *extraout_EAX_00 = (uint)local_60;
        extraout_EAX_00[1] = (uint)local_5c;
        extraout_EAX_00[2] = (uint)local_60;
        extraout_EAX_00[3] = 0xffffffff;
        extraout_EAX_00[4] = 0xffffffff;
        extraout_EAX_00[5] = 0xffffffff;
        local_54 = extraout_EAX_00;
      }
      CFastVB__Helper_00573170(local_1c,local_14,&local_54,unaff_EDI);
      CFastVB__StampRecordOwnerFields(piVar1,(int)local_54,(int)unaff_EDI);
      local_50 = puVar3;
      CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_50,unaff_EDI);
      local_58 = puVar3;
      piVar1[10] = piVar1[10] + 1;
    }
    CFastVB__Helper_00573170(local_1c,local_14,&local_6c,unaff_EDI);
    CFastVB__Helper_00573170(local_2c,local_24,&local_6c,unaff_EDI);
    CFastVB__StampRecordOwnerFields(piVar1,(int)local_6c,(int)unaff_EDI);
    local_50 = puVar11;
    CFastVB__Helper_00572fa0(local_4c,(int)local_44,&local_50,unaff_EDI);
    local_60 = local_58;
    local_5c = puVar11;
    puVar3 = (uint *)CFastVB__ResolveOppositeAdjacencyRecord
                               ((int)param_1,(int)local_58,(int)puVar11,(int)local_6c);
    piVar1 = local_68;
  }
  CTexture__Helper_005708a0(piVar1,(int)local_3c,(int)local_1c,(int)unaff_EDI);
  local_4._0_1_ = 2;
  CFastVB__ReleaseBufferAndResetTriplet_0056f260((int)local_2c);
  local_4._0_1_ = 1;
  CFastVB__ReleaseBufferAndResetTriplet_0056f260((int)local_1c);
  local_4 = (uint)local_4._1_3_ << 8;
  CFastVB__ReleaseBufferAndResetTriplet_0056f260((int)local_3c);
  local_4 = 0xffffffff;
  CFastVB__ReleaseBufferAndResetTriplet_0056f260((int)local_4c);
  ExceptionList = local_c;
  return;
}
