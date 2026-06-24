/* address: 0x004e1ab0 */
/* name: CMonitor__Helper_004e1ab0 */
/* signature: int __thiscall CMonitor__Helper_004e1ab0(void * this, int param_1, int param_2, int param_3) */


int __thiscall CMonitor__Helper_004e1ab0(void *this,int param_1,int param_2,int param_3)

{
  int *piVar1;
  int iVar2;

  do {
    if (param_1 == 0) {
      return 0;
    }
    if (*(char *)((int)this + 4) != '\0') {
      for (piVar1 = *(int **)((int)this + 0xc); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[0x1d])
      {
        if ((((char)piVar1[2] != '\0') && (*piVar1 == param_2)) &&
           (iVar2 = stricmp((char *)(piVar1[3] + 8),(char *)(param_1 + 0x40)), iVar2 == 0)) {
          return 1;
        }
      }
    }
    param_1 = *(int *)(param_1 + 0xd4);
  } while( true );
}
