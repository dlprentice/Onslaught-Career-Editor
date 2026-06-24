/* address: 0x005710d0 */
/* name: CFastVB__EmitTriangleStripIndexBuffer */
/* signature: void __stdcall CFastVB__EmitTriangleStripIndexBuffer(int param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Removing unreachable block (ram,0x0057150f) */
/* WARNING: Removing unreachable block (ram,0x00571526) */
/* WARNING: Removing unreachable block (ram,0x00571535) */
/* WARNING: Removing unreachable block (ram,0x0057153e) */
/* WARNING: Type propagation algorithm not settling */

void CFastVB__EmitTriangleStripIndexBuffer(int param_1,int param_2,int param_3,void *param_4)

{
  int this;
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  void *extraout_EAX;
  uint uVar5;
  void *unaff_EBP;
  void *pvVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_40;
  void *local_3c;
  int local_38;
  int local_34;
  int local_30 [12];

  this = param_2;
  local_30[6] = 0;
  local_30[8] = 0;
  local_30[9] = 0xffffffff;
  local_30[10] = 0xffffffff;
  local_30[0xb] = 0xffffffff;
  if (*(int *)(param_1 + 4) == 0) {
    local_4c = 0;
  }
  else {
    local_4c = *(int *)(param_1 + 8) - *(int *)(param_1 + 4) >> 2;
  }
  local_48 = 0;
  local_50 = 0;
  if (0 < local_4c) {
    do {
      iVar4 = *(int *)(*(int *)(param_1 + 4) + local_50 * 4);
      if (*(int *)(iVar4 + 0x10) == 0) {
        local_54 = 0;
      }
      else {
        local_54 = *(int *)(iVar4 + 0x14) - *(int *)(iVar4 + 0x10) >> 2;
      }
      piVar7 = *(int **)(iVar4 + 0x10);
      piVar9 = (int *)*piVar7;
      local_3c = (void *)piVar9[2];
      iVar3 = piVar9[1];
      local_30[0] = *piVar9;
      local_30[3] = 0xffffffff;
      local_30[4] = 0xffffffff;
      local_30[5] = 0xffffffff;
      param_2 = iVar3;
      local_30[1] = iVar3;
      local_30[2] = (int)local_3c;
      local_30[7] = local_30[8];
      if (1 < local_54) {
        iVar2 = CFastVB__AreTriangleVertexSetsEquivalent((void *)piVar7[1],local_30);
        if (iVar2 == iVar3) {
          local_30[1] = local_30[0];
          iVar8 = local_30[0];
          local_30[0] = iVar3;
        }
        else {
          iVar8 = iVar3;
          if ((void *)iVar2 == local_3c) {
            local_30[2] = local_30[0];
            local_30[0] = (int)local_3c;
          }
        }
        iVar3 = iVar8;
        if (2 < local_54) {
          bVar1 = CFastVB__Helper_00571870((void *)piVar7[1]);
          piVar7 = *(int **)(iVar4 + 0x10);
          if (bVar1) {
            bVar1 = local_30[1] == *(int *)(piVar7[1] + 4);
          }
          else {
            CFastVB__GetSharedVerticesBetweenTriangles
                      ((void *)piVar7[2],local_30,&local_38,&local_34);
            iVar3 = local_30[1];
            if (local_38 != local_30[1]) goto LAB_0057122c;
            bVar1 = local_34 == -1;
          }
          iVar2 = local_30[2];
          iVar3 = local_30[1];
          if (bVar1) {
            local_30[1] = local_30[2];
            local_30[2] = iVar3;
            iVar3 = iVar2;
          }
        }
      }
LAB_0057122c:
      if ((local_50 == 0) || ((char)param_3 == '\0')) {
        bVar1 = CFastVB__IsDirectedEdgeInTriangle((void *)*piVar7,local_30[0],iVar3);
        if (!bVar1) {
          iVar3 = *(int *)(this + 8);
          goto LAB_005712c4;
        }
      }
      else {
        CFastVB__Helper_005736d0
                  ((void *)this,*(int *)(this + 8),(void *)0x1,(uint)local_30,unaff_EBP);
        if (*(int *)(this + 4) == 0) {
          iVar3 = 0;
        }
        else {
          iVar3 = *(int *)(this + 8) - *(int *)(this + 4) >> 2;
        }
        bVar1 = CFastVB__IsEven(iVar3 - local_48);
        param_2 = CONCAT31(param_2._1_3_,bVar1);
        bVar1 = CFastVB__IsDirectedEdgeInTriangle
                          ((void *)**(undefined4 **)(iVar4 + 0x10),local_30[0],local_30[1]);
        if ((bool)(char)param_2 != bVar1) {
          iVar3 = *(int *)(this + 8);
LAB_005712c4:
          CFastVB__Helper_005736d0((void *)this,iVar3,(void *)0x1,(uint)local_30,unaff_EBP);
        }
      }
      CFastVB__Helper_005736d0((void *)this,*(int *)(this + 8),(void *)0x1,(uint)local_30,unaff_EBP)
      ;
      CFastVB__Helper_005736d0
                ((void *)this,*(int *)(this + 8),(void *)0x1,(uint)(local_30 + 1),unaff_EBP);
      CFastVB__Helper_005736d0
                ((void *)this,*(int *)(this + 8),(void *)0x1,(uint)(local_30 + 2),unaff_EBP);
      piVar7 = local_30;
      piVar9 = local_30 + 6;
      for (iVar3 = 6; iVar3 != 0; iVar3 = iVar3 + -1) {
        *piVar9 = *piVar7;
        piVar7 = piVar7 + 1;
        piVar9 = piVar9 + 1;
      }
      iVar3 = 1;
      if (1 < local_54) {
        do {
          iVar2 = *(int *)(iVar4 + 0x10);
          local_40 = CFastVB__AreTriangleVertexSetsEquivalent
                               (local_30 + 6,*(void **)(iVar2 + iVar3 * 4));
          if (local_40 == -1) {
            CFastVB__Helper_005736d0
                      ((void *)this,*(int *)(this + 8),(void *)0x1,*(int *)(iVar2 + iVar3 * 4) + 8,
                       unaff_EBP);
            local_30[6] = **(int **)(*(int *)(iVar4 + 0x10) + iVar3 * 4);
            local_30[7] = *(int *)(*(int *)(*(int *)(iVar4 + 0x10) + iVar3 * 4) + 4);
            local_30[8] = *(int *)(*(int *)(*(int *)(iVar4 + 0x10) + iVar3 * 4) + 8);
          }
          else {
            CFastVB__Helper_005736d0
                      ((void *)this,*(int *)(this + 8),(void *)0x1,(uint)&local_40,unaff_EBP);
            local_30[6] = local_30[7];
            local_30[7] = local_30[8];
            local_30[8] = local_40;
          }
          iVar3 = iVar3 + 1;
        } while (iVar3 < local_54);
      }
      if ((char)param_3 == '\0') {
        piVar7 = *(int **)(this + 8);
        param_2 = -1;
        if (*(int *)(this + 0xc) - (int)piVar7 >> 2 == 0) {
          iVar4 = *(int *)(this + 4);
          if ((iVar4 == 0) || (uVar5 = (int)piVar7 - iVar4 >> 2, uVar5 < 2)) {
            uVar5 = 1;
          }
          if (iVar4 == 0) {
            iVar4 = 0;
          }
          else {
            iVar4 = (int)piVar7 - iVar4 >> 2;
          }
          iVar4 = iVar4 + uVar5;
          iVar3 = iVar4;
          if (iVar4 < 0) {
            iVar3 = 0;
          }
          CFastVB__Helper_00426fd0(iVar3 * 4);
          pvVar6 = extraout_EAX;
          local_3c = extraout_EAX;
          for (piVar9 = *(int **)(this + 4); piVar9 != piVar7; piVar9 = piVar9 + 1) {
            CFastVB__Helper_00574230(pvVar6,piVar9);
            pvVar6 = (void *)((int)pvVar6 + 4);
          }
          CTexture__Helper_00573ff0(pvVar6,1,&param_2);
          CFastVB__Helper_00572f50(piVar7,*(void **)(this + 8),(void *)((int)pvVar6 + 4));
          VFuncSlot_12_00405db0();
          OID__FreeObject_Callback(*(void **)(this + 4));
          *(void **)(this + 0xc) = (void *)((int)local_3c + iVar4 * 4);
          iVar4 = CFastVB__CountDwordsFromPointerSpan(this);
          *(void **)(this + 4) = local_3c;
          *(int *)(this + 8) = (int)local_3c + iVar4 * 4 + 4;
        }
        else {
          CFastVB__Helper_00572f50(piVar7,piVar7,piVar7 + 1);
          CTexture__Helper_00573ff0
                    (*(void **)(this + 8),1 - ((int)*(void **)(this + 8) - (int)piVar7 >> 2),
                     &param_2);
          piVar9 = *(int **)(this + 8);
          for (; piVar7 != piVar9; piVar7 = piVar7 + 1) {
            *piVar7 = param_2;
          }
          *(int *)(this + 8) = *(int *)(this + 8) + 4;
        }
        local_48 = local_48 + 1;
        *(int *)param_4 = *(int *)param_4 + 1;
      }
      else if (local_50 != local_4c + -1) {
        CFastVB__Helper_005736d0
                  ((void *)this,*(int *)(this + 8),(void *)0x1,(uint)(local_30 + 8),unaff_EBP);
      }
      local_30[6] = local_30[7];
      local_50 = local_50 + 1;
    } while (local_50 < local_4c);
  }
  if ((char)param_3 != '\0') {
    *(undefined4 *)param_4 = 1;
  }
  return;
}
