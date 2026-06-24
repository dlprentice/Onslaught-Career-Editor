/* address: 0x004304d0 */
/* name: CSpawnerStatement__VFunc_01_004304d0 */
/* signature: void __fastcall CSpawnerStatement__VFunc_01_004304d0(int param_1) */


void __fastcall CSpawnerStatement__VFunc_01_004304d0(int param_1)

{
  void *pvVar1;
  int iVar2;
  int *piVar3;
  void *this;
  int unaff_EDI;

  pvVar1 = (void *)(param_1 + 0xc);
  CSpawnerData__ctor_like_00430510(pvVar1);
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
