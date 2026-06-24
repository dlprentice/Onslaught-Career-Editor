/* address: 0x00591280 */
/* name: CDXTexture__Unk_00591280 */
/* signature: int __stdcall CDXTexture__Unk_00591280(void * param_1) */


int CDXTexture__Unk_00591280(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;

  iVar2 = *(int *)((int)param_1 + 0x14);
  if (((iVar2 == 0xcd) || (iVar2 == 0xce)) && (*(int *)((int)param_1 + 0x40) == 0)) {
    if (*(uint *)((int)param_1 + 0x8c) < *(uint *)((int)param_1 + 0x74)) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 0x43;
      (*(code *)*puVar1)(param_1);
    }
    (**(code **)(*(int *)((int)param_1 + 0x1a8) + 4))(param_1);
    *(undefined4 *)((int)param_1 + 0x14) = 0xd2;
  }
  else if (iVar2 == 0xcf) {
    *(undefined4 *)((int)param_1 + 0x14) = 0xd2;
  }
  else if (iVar2 != 0xd2) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 0x14;
    puVar1[6] = iVar2;
    (*(code *)*puVar1)(param_1);
  }
  iVar2 = *(int *)(*(int *)((int)param_1 + 0x1b8) + 0x14);
  while( true ) {
    if (iVar2 != 0) {
      (**(code **)(*(int *)((int)param_1 + 0x18) + 0x18))(param_1);
      CDXTexture__Unk_0059c5d0((int)param_1);
      return 1;
    }
    iVar2 = (*(code *)**(undefined4 **)((int)param_1 + 0x1b8))(param_1);
    if (iVar2 == 0) break;
    iVar2 = *(int *)(*(int *)((int)param_1 + 0x1b8) + 0x14);
  }
  return 0;
}
