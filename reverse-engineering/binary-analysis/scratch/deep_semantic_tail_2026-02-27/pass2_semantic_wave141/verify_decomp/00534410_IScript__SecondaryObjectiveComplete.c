/* address: 0x00534410 */
/* name: IScript__SecondaryObjectiveComplete */
/* signature: void __stdcall IScript__SecondaryObjectiveComplete(void * param_1) */


void IScript__SecondaryObjectiveComplete(void *param_1)

{
  undefined4 uVar1;
  int iVar2;

  uVar1 = (**(code **)(**(int **)((int)param_1 + 4) + 0x30))();
  iVar2 = (**(code **)(**(int **)param_1 + 0x30))();
  *(undefined4 *)(&DAT_008a9b30 + iVar2 * 8) = uVar1;
  *(undefined4 *)(&DAT_008a9b2c + iVar2 * 8) = 1;
  return;
}
