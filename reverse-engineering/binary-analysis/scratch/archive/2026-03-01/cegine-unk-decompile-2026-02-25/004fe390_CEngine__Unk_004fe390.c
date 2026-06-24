/* address: 0x004fe390 */
/* name: CEngine__Unk_004fe390 */
/* signature: void __thiscall CEngine__Unk_004fe390(void * this, int param_1, void * param_2) */


void __thiscall CEngine__Unk_004fe390(void *this,int param_1,void *param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;

  piVar1 = *(int **)((int)this + 0x18c);
  if (piVar1 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *piVar1;
  }
  while (iVar3 != 0) {
    iVar2 = stricmp((char *)param_1,*(char **)(*(int *)(iVar3 + 0x3d0) + 8));
    if (iVar2 == 0) {
      *(undefined4 *)(iVar3 + 0x3f4) = 1;
    }
    piVar1 = (int *)piVar1[1];
    if (piVar1 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      iVar3 = *piVar1;
    }
  }
  return;
}
