/* address: 0x004e6610 */
/* name: CExplosionInitThing__HasSpawnDelayElapsedAndNotTriggered */
/* signature: int __fastcall CExplosionInitThing__HasSpawnDelayElapsedAndNotTriggered(int param_1) */


int __fastcall CExplosionInitThing__HasSpawnDelayElapsedAndNotTriggered(int param_1)

{
  if ((DAT_00672fd0 < *(float *)(param_1 + 0x88)) && (*(int *)(param_1 + 0x7c) == 0)) {
    return 1;
  }
  return 0;
}
