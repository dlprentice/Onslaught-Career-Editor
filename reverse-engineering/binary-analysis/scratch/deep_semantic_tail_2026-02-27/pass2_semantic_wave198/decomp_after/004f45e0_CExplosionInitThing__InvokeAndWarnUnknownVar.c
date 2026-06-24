/* address: 0x004f45e0 */
/* name: CExplosionInitThing__InvokeAndWarnUnknownVar */
/* signature: void __stdcall CExplosionInitThing__InvokeAndWarnUnknownVar(void * param_1) */


void CExplosionInitThing__InvokeAndWarnUnknownVar(void *param_1)

{
  (**(code **)(*(int *)param_1 + 0x38))();
  CConsole__Printf(&DAT_0066f580,s_Warning__Uknown_var___s__in_call_006331ec);
  return;
}
