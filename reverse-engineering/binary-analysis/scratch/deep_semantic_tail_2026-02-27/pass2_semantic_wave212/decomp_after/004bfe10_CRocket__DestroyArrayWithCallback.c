/* address: 0x004bfe10 */
/* name: CRocket__DestroyArrayWithCallback */
/* signature: void __fastcall CRocket__DestroyArrayWithCallback(void * param_1) */


void __fastcall CRocket__DestroyArrayWithCallback(void *param_1)

{
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d3f88;
  pvStack_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &pvStack_c;
  CDXLandscape__DestroyArrayWithCallback
            ((int)param_1 + 0xec,8,4,CParticleManager__RemoveFromGlobalList);
  local_4 = 0xffffffff;
  CActor__ctor_like_004013d0(param_1);
  ExceptionList = pvStack_c;
  return;
}
