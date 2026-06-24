/* address: 0x004adf90 */
/* name: CExplosionInitThing__Unk_004adf90 */
/* signature: void __fastcall CExplosionInitThing__Unk_004adf90(void * param_1) */


void __fastcall CExplosionInitThing__Unk_004adf90(void *param_1)

{
  if (*(int *)((int)param_1 + 8) != 0) {
    if (*(void **)((int)param_1 + 0xc) != (void *)0x0) {
      OID__FreeObject(*(void **)((int)param_1 + 0xc));
      *(undefined4 *)((int)param_1 + 0xc) = 0;
    }
    *(undefined4 *)((int)param_1 + 0x10) = 0;
    *(undefined4 *)((int)param_1 + 0x14) = 0;
    *(undefined4 *)((int)param_1 + 0x18) = 0;
    *(undefined4 *)((int)param_1 + 0x1c) = 0;
    *(undefined4 *)((int)param_1 + 8) = 0;
  }
  if (*(int *)param_1 != 0) {
    CUnit__Unk_004f27e0(*(int *)param_1 + 8);
    *(undefined4 *)param_1 = 0;
  }
  if (*(int *)((int)param_1 + 4) != 0) {
    CEngine__Unk_00501310(*(int *)((int)param_1 + 4));
    *(undefined4 *)((int)param_1 + 4) = 0;
  }
  return;
}
