/* address: 0x004d9ef0 */
/* name: CEngine__Unk_004d9ef0 */
/* signature: void __fastcall CEngine__Unk_004d9ef0(void * param_1) */


void __fastcall CEngine__Unk_004d9ef0(void *param_1)

{
  int unaff_ESI;

  CEngine__Unk_004db630((int)param_1);
  CUnit__Unk_00402010((int)param_1);
  if ((*(int *)(*(int *)((int)param_1 + 0xf0) + 0x5c) == 0) &&
     (*(int *)(*(int *)((int)param_1 + 0xf0) + 0x6c) == 0)) {
    CExplosionInitThing__ctor_like_004d9f30(param_1,2,0,0,unaff_ESI);
    (**(code **)(*(int *)param_1 + 200))();
  }
  return;
}
