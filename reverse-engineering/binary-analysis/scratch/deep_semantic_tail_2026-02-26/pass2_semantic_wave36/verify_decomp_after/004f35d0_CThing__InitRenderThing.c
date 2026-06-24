/* address: 0x004f35d0 */
/* name: CThing__InitRenderThing */
/* signature: void __fastcall CThing__InitRenderThing(void * param_1) */


void __fastcall CThing__InitRenderThing(void *param_1)

{
  int owner_tag;
  void *pvVar1;

  if (param_1 == (void *)0x0) {
    owner_tag = 0;
  }
  else {
    owner_tag = (int)param_1 + 8;
  }
  pvVar1 = (void *)(**(code **)(*(int *)param_1 + 0x20))();
  pvVar1 = CResourceDescriptorTable__InstantiateChain(pvVar1,owner_tag);
  *(void **)((int)param_1 + 0x30) = pvVar1;
  return;
}
