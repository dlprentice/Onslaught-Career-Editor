/* address: 0x00580eef */
/* name: CFastVB__ShutdownActiveProfile_Thunk */
/* signature: int __fastcall CFastVB__ShutdownActiveProfile_Thunk(void * param_1) */


int __fastcall CFastVB__ShutdownActiveProfile_Thunk(void *param_1)

{
  int *piVar1;

  piVar1 = *(int **)param_1;
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 0x28))(piVar1);
    piVar1 = *(int **)param_1;
    if (piVar1 != (int *)0x0) {
      (**(code **)(*piVar1 + 8))(piVar1);
      *(undefined4 *)param_1 = 0;
    }
  }
  return 0;
}
