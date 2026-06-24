/* address: 0x00490f40 */
/* name: CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap */
/* signature: void __fastcall CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap(int param_1) */


void __fastcall CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap(int param_1)

{
  CUnitAI__FreeOwnedObjects_24_1028(param_1);
  CMixerMap__Destroy();
  return;
}
