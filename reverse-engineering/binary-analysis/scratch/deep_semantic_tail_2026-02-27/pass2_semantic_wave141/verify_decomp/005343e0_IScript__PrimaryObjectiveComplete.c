/* address: 0x005343e0 */
/* name: IScript__PrimaryObjectiveComplete */
/* signature: void __stdcall IScript__PrimaryObjectiveComplete(void * param_1) */


void IScript__PrimaryObjectiveComplete(void *param_1)

{
  undefined4 uVar1;
  int iVar2;

  uVar1 = (**(code **)(**(int **)((int)param_1 + 4) + 0x30))();
  iVar2 = (**(code **)(**(int **)param_1 + 0x30))();
  *(undefined4 *)(&DAT_008a9ae0 + iVar2 * 8) = uVar1;
  *(undefined4 *)(&DAT_008a9adc + iVar2 * 8) = 1;
  return;
}
