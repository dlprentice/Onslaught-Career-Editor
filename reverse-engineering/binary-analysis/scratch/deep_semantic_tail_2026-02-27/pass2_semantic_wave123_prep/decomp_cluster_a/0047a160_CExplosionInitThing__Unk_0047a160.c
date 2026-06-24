/* address: 0x0047a160 */
/* name: CExplosionInitThing__Unk_0047a160 */
/* signature: void __fastcall CExplosionInitThing__Unk_0047a160(void * param_1) */


void __fastcall CExplosionInitThing__Unk_0047a160(void *param_1)

{
  if ((*(int *)((int)param_1 + 0x244) != 1) && (*(int *)((int)param_1 + 0x244) != 2)) {
    (**(code **)(*(int *)param_1 + 0xf4))
              (*(undefined4 *)((int)param_1 + 0x278),*(undefined4 *)((int)param_1 + 0x27c),
               *(undefined4 *)((int)param_1 + 0x280),*(undefined4 *)((int)param_1 + 0x284),0);
    *(undefined4 *)((int)param_1 + 0x244) = 1;
  }
  return;
}
