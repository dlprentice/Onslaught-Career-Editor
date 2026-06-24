/* address: 0x0042f5b0 */
/* name: CWeaponStatement__VFunc_01_0042f5b0 */
/* signature: void __fastcall CWeaponStatement__VFunc_01_0042f5b0(int param_1) */


void __fastcall CWeaponStatement__VFunc_01_0042f5b0(int param_1)

{
  void *pvVar1;
  int iVar2;
  int *piVar3;
  void *this;
  int unaff_EDI;

  pvVar1 = (void *)(param_1 + 0xc);
  CWeaponStatement__Create(pvVar1);
  iVar2 = *(int *)(param_1 + 0x10c);
  piVar3 = *(int **)(iVar2 + 4);
  if (piVar3 != (int *)0x0) {
    (**(code **)(*piVar3 + 4))(pvVar1);
  }
  this = *(void **)(iVar2 + 8);
  if (this != (void *)0x0) {
    CUnitAI__Unk_00430fa0(this,(int)pvVar1,unaff_EDI);
  }
  return;
}
