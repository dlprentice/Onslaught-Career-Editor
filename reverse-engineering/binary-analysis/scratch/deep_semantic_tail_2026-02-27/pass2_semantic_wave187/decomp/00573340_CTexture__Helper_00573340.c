/* address: 0x00573340 */
/* name: CTexture__Helper_00573340 */
/* signature: void __thiscall CTexture__Helper_00573340(void * this, int param_1, void * param_2, void * param_3) */


void __thiscall CTexture__Helper_00573340(void *this,int param_1,void *param_2,void *param_3)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  int *piVar6;
  int *piVar7;
  undefined4 *extraout_EAX;
  undefined4 *puVar8;
  void *unaff_EDI;
  bool bVar9;
  int *local_4;

  bVar9 = true;
  piVar1 = *(int **)((int)this + 4);
  piVar6 = piVar1;
  piVar7 = (int *)piVar1[1];
  while (piVar7 != DAT_009d0c44) {
    bVar9 = *(uint *)param_2 < (uint)piVar7[3];
    piVar6 = piVar7;
    if (bVar9) {
      piVar7 = (int *)*piVar7;
    }
    else {
      piVar7 = (int *)piVar7[2];
    }
  }
  if (*(char *)((int)this + 8) != '\0') {
    local_4 = this;
    CTexture__InitTreeNodeParentAndKey((int)piVar6,0);
    *extraout_EAX = DAT_009d0c44;
    extraout_EAX[2] = DAT_009d0c44;
    CFastVB__AssignDwordIfDestNotNull(extraout_EAX + 3,param_2);
    *(int *)((int)this + 0xc) = *(int *)((int)this + 0xc) + 1;
    if (((piVar6 == *(int **)((int)this + 4)) || (piVar7 != DAT_009d0c44)) ||
       (*(uint *)param_2 < (uint)piVar6[3])) {
      *piVar6 = (int)extraout_EAX;
      piVar1 = *(int **)((int)this + 4);
      if (piVar6 == piVar1) {
        piVar1[1] = (int)extraout_EAX;
        *(undefined4 **)(*(int *)((int)this + 4) + 8) = extraout_EAX;
      }
      else if (piVar6 == (int *)*piVar1) {
        *piVar1 = (int)extraout_EAX;
      }
    }
    else {
      piVar6[2] = (int)extraout_EAX;
      if (piVar6 == *(int **)(*(int *)((int)this + 4) + 8)) {
        *(undefined4 **)(*(int *)((int)this + 4) + 8) = extraout_EAX;
      }
    }
    puVar8 = extraout_EAX;
    if (extraout_EAX != *(undefined4 **)(*(int *)((int)this + 4) + 4)) {
      do {
        puVar2 = (undefined4 *)puVar8[1];
        if (puVar2[4] != 0) break;
        puVar3 = *(undefined4 **)puVar2[1];
        if (puVar2 == puVar3) {
          iVar4 = ((undefined4 *)puVar2[1])[2];
          if (*(int *)(iVar4 + 0x10) == 0) {
            puVar2[4] = 1;
            *(undefined4 *)(iVar4 + 0x10) = 1;
            *(undefined4 *)(*(int *)(puVar8[1] + 4) + 0x10) = 0;
            puVar8 = *(undefined4 **)(puVar8[1] + 4);
          }
          else {
            if (puVar8 == (undefined4 *)puVar2[2]) {
              CTexture__Helper_00574020(this,(int)puVar2,(int)unaff_EDI);
              puVar8 = puVar2;
            }
            *(undefined4 *)(puVar8[1] + 0x10) = 1;
            *(undefined4 *)(*(int *)(puVar8[1] + 4) + 0x10) = 0;
            CTexture__RotateTreeLeft(this,*(int *)(puVar8[1] + 4),unaff_EDI);
          }
        }
        else if (puVar3[4] == 0) {
          puVar2[4] = 1;
          puVar3[4] = 1;
          *(undefined4 *)(*(int *)(puVar8[1] + 4) + 0x10) = 0;
          puVar8 = *(undefined4 **)(puVar8[1] + 4);
        }
        else {
          if (puVar8 == (undefined4 *)*puVar2) {
            CTexture__RotateTreeLeft(this,(int)puVar2,unaff_EDI);
            puVar8 = puVar2;
          }
          *(undefined4 *)(puVar8[1] + 0x10) = 1;
          *(undefined4 *)(*(int *)(puVar8[1] + 4) + 0x10) = 0;
          CTexture__Helper_00574020(this,*(int *)(puVar8[1] + 4),(int)unaff_EDI);
        }
      } while (puVar8 != *(undefined4 **)(*(int *)((int)this + 4) + 4));
    }
    *(undefined4 *)(*(int *)(*(int *)((int)this + 4) + 4) + 0x10) = 1;
    *(undefined4 **)param_1 = extraout_EAX;
    *(undefined1 *)(param_1 + 4) = 1;
    return;
  }
  local_4 = piVar6;
  if (bVar9) {
    if (piVar6 == (int *)*piVar1) goto LAB_00573526;
    CTexture__TreeIteratorNext(&local_4);
  }
  if (*(uint *)param_2 <= (uint)local_4[3]) {
    *(undefined1 *)(param_1 + 4) = 0;
    *(int **)param_1 = local_4;
    return;
  }
LAB_00573526:
  puVar8 = (undefined4 *)CTexture__InsertNodeIntoTree();
  uVar5 = *puVar8;
  *(undefined1 *)(param_1 + 4) = 1;
  *(undefined4 *)param_1 = uVar5;
  return;
}
