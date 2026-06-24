/* address: 0x005809de */
/* name: CFastVB__Unk_005809de */
/* signature: int __fastcall CFastVB__Unk_005809de(void * param_1) */


int __fastcall CFastVB__Unk_005809de(void *param_1)

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
