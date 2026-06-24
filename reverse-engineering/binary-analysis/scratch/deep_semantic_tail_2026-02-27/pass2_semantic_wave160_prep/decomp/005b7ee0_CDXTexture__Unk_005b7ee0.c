/* address: 0x005b7ee0 */
/* name: CDXTexture__Unk_005b7ee0 */
/* signature: void __stdcall CDXTexture__Unk_005b7ee0(void * param_1) */


void CDXTexture__Unk_005b7ee0(void *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;

  iVar1 = *(int *)((int)param_1 + 0x154);
  iVar2 = *(int *)(iVar1 + 0x14);
  if (iVar2 == 0) {
    CDXTexture__Unk_005b7c50();
    CDXTexture__Unk_005b7d30();
    if (*(int *)((int)param_1 + 0xb0) == 0) {
      (*(code *)**(undefined4 **)((int)param_1 + 0x168))(param_1);
      (*(code *)**(undefined4 **)((int)param_1 + 0x16c))(param_1);
      (*(code *)**(undefined4 **)((int)param_1 + 0x15c))(param_1,0);
    }
    (*(code *)**(undefined4 **)((int)param_1 + 0x170))(param_1);
    (*(code *)**(undefined4 **)((int)param_1 + 0x174))(param_1,*(undefined4 *)((int)param_1 + 0xb8))
    ;
    (*(code *)**(undefined4 **)((int)param_1 + 0x160))
              (param_1,(*(int *)(iVar1 + 0x1c) < 2) - 1U & 3);
    (*(code *)**(undefined4 **)((int)param_1 + 0x158))(param_1,0);
    *(uint *)(iVar1 + 0xc) = (uint)(*(int *)((int)param_1 + 0xb8) == 0);
  }
  else {
    if (iVar2 == 1) {
      CDXTexture__Unk_005b7c50();
      CDXTexture__Unk_005b7d30();
      if (((*(int *)((int)param_1 + 0x144) != 0) || (*(int *)((int)param_1 + 0x14c) == 0)) ||
         (*(int *)((int)param_1 + 0xb4) != 0)) {
        (*(code *)**(undefined4 **)((int)param_1 + 0x174))(param_1,1);
        (*(code *)**(undefined4 **)((int)param_1 + 0x160))(param_1,2);
        *(undefined4 *)(iVar1 + 0xc) = 0;
        goto LAB_005b8033;
      }
      *(undefined4 *)(iVar1 + 0x14) = 2;
      *(int *)(iVar1 + 0x18) = *(int *)(iVar1 + 0x18) + 1;
    }
    else if (iVar2 != 2) {
      puVar3 = *(undefined4 **)param_1;
      puVar3[5] = 0x30;
      (*(code *)*puVar3)(param_1);
      goto LAB_005b8033;
    }
    if (*(int *)((int)param_1 + 0xb8) == 0) {
      CDXTexture__Unk_005b7c50();
      CDXTexture__Unk_005b7d30();
    }
    (*(code *)**(undefined4 **)((int)param_1 + 0x174))(param_1,0);
    (*(code *)**(undefined4 **)((int)param_1 + 0x160))(param_1,2);
    if (*(int *)(iVar1 + 0x20) == 0) {
      (**(code **)(*(int *)((int)param_1 + 0x164) + 4))(param_1);
    }
    (**(code **)(*(int *)((int)param_1 + 0x164) + 8))(param_1);
    *(undefined4 *)(iVar1 + 0xc) = 0;
  }
LAB_005b8033:
  iVar2 = *(int *)((int)param_1 + 8);
  *(uint *)(iVar1 + 0x10) = (uint)(*(int *)(iVar1 + 0x18) == *(int *)(iVar1 + 0x1c) + -1);
  if (iVar2 != 0) {
    *(int *)(iVar2 + 0xc) = *(int *)(iVar1 + 0x18);
    *(undefined4 *)(iVar2 + 0x10) = *(undefined4 *)(iVar1 + 0x1c);
  }
  return;
}
