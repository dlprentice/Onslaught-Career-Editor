/* address: 0x004e1880 */
/* name: CMonitor__FindSoundEventByOwnerAndName */
/* signature: int * __thiscall CMonitor__FindSoundEventByOwnerAndName(void * this, int param_1, void * param_2, int param_3) */


int * __thiscall
CMonitor__FindSoundEventByOwnerAndName(void *this,int param_1,void *param_2,int param_3)

{
  int *piVar1;
  int iVar2;

  if (*(char *)((int)this + 4) != '\0') {
    for (piVar1 = *(int **)((int)this + 0xc); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[0x1d]) {
      if ((((char)piVar1[2] != '\0') && ((void *)*piVar1 == param_2)) &&
         (iVar2 = stricmp((char *)(piVar1[3] + 8),(char *)param_1), iVar2 == 0)) {
        return piVar1;
      }
    }
  }
  return (int *)0x0;
}
