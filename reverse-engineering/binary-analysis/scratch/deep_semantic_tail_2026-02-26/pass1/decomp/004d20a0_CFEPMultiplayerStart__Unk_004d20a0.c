/* address: 0x004d20a0 */
/* name: CFEPMultiplayerStart__Unk_004d20a0 */
/* signature: void __fastcall CFEPMultiplayerStart__Unk_004d20a0(void * param_1) */


void __fastcall CFEPMultiplayerStart__Unk_004d20a0(void *param_1)

{
  CFEPMultiplayerStart__Helper_00403730(param_1);
  if (*(int *)(*(int *)((int)param_1 + 0x164) + 0x11c) == 0) {
    CExplosionInitThing__ctor_like_004fd230(param_1);
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}
