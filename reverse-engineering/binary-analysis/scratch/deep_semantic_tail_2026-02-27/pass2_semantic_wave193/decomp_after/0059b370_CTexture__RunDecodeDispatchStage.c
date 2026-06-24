/* address: 0x0059b370 */
/* name: CTexture__RunDecodeDispatchStage */
/* signature: void __stdcall CTexture__RunDecodeDispatchStage(void * param_1) */


void CTexture__RunDecodeDispatchStage(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;

  iVar1 = *(int *)((int)param_1 + 0x1a8);
  if (*(int *)(iVar1 + 8) == 0) {
    if ((*(int *)((int)param_1 + 0x54) != 0) && (*(int *)((int)param_1 + 0x88) == 0)) {
      if ((*(int *)((int)param_1 + 0x5c) == 0) || (*(int *)((int)param_1 + 0x6c) == 0)) {
        if (*(int *)((int)param_1 + 100) == 0) {
          puVar2 = *(undefined4 **)param_1;
          puVar2[5] = 0x2e;
          (*(code *)*puVar2)(param_1);
        }
        else {
          *(undefined4 *)((int)param_1 + 0x1d0) = *(undefined4 *)(iVar1 + 0x14);
        }
      }
      else {
        *(undefined4 *)((int)param_1 + 0x1d0) = *(undefined4 *)(iVar1 + 0x18);
        *(undefined4 *)(iVar1 + 8) = 1;
      }
    }
    (*(code *)**(undefined4 **)((int)param_1 + 0x1c4))(param_1);
    (**(code **)(*(int *)((int)param_1 + 0x1b0) + 8))(param_1);
    if (*(int *)((int)param_1 + 0x44) == 0) {
      if (*(int *)(iVar1 + 0x10) == 0) {
        (*(code *)**(undefined4 **)((int)param_1 + 0x1cc))(param_1);
      }
      (*(code *)**(undefined4 **)((int)param_1 + 0x1c8))(param_1);
      if (*(int *)((int)param_1 + 0x54) != 0) {
        (*(code *)**(undefined4 **)((int)param_1 + 0x1d0))(param_1,*(undefined4 *)(iVar1 + 8));
      }
      (*(code *)**(undefined4 **)((int)param_1 + 0x1b4))(param_1,-(*(int *)(iVar1 + 8) != 0) & 3);
      (*(code *)**(undefined4 **)((int)param_1 + 0x1ac))(param_1,0);
    }
  }
  else {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x30;
    (*(code *)*puVar2)(param_1);
  }
  iVar3 = *(int *)((int)param_1 + 8);
  if (iVar3 != 0) {
    *(undefined4 *)(iVar3 + 0xc) = *(undefined4 *)(iVar1 + 0xc);
    iVar4 = (*(int *)(iVar1 + 8) != 0) + 1 + *(int *)(iVar1 + 0xc);
    iVar1 = *(int *)((int)param_1 + 0x40);
    *(int *)(iVar3 + 0x10) = iVar4;
    if ((iVar1 != 0) && (*(int *)(*(int *)((int)param_1 + 0x1b8) + 0x14) == 0)) {
      *(uint *)(iVar3 + 0x10) = (*(int *)((int)param_1 + 0x6c) != 0) + 1 + iVar4;
    }
  }
  return;
}
