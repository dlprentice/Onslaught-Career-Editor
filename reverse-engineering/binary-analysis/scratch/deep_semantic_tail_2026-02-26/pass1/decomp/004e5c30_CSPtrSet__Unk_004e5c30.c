/* address: 0x004e5c30 */
/* name: CSPtrSet__Unk_004e5c30 */
/* signature: int __thiscall CSPtrSet__Unk_004e5c30(void * this, void * param_1, int param_2) */


int __thiscall CSPtrSet__Unk_004e5c30(void *this,void *param_1,int param_2)

{
  int *piVar1;
  void *pvVar2;

  piVar1 = *(int **)this;
  if (piVar1 != (int *)0x0) {
    pvVar2 = (void *)*piVar1;
    while (pvVar2 != (void *)0x0) {
      if (pvVar2 == param_1) {
        return 1;
      }
      piVar1 = (int *)piVar1[1];
      if (piVar1 == (int *)0x0) {
        return 0;
      }
      pvVar2 = (void *)*piVar1;
    }
  }
  return 0;
}
