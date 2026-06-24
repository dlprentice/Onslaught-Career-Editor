/* address: 0x004f7440 */
/* name: CMissionScriptObjectCode__FreeObjectIfPresent */
/* signature: void __fastcall CMissionScriptObjectCode__FreeObjectIfPresent(void * param_1) */


void __fastcall CMissionScriptObjectCode__FreeObjectIfPresent(void *param_1)

{
  OID__FreeObject(*(void **)param_1);
  OID__FreeObject(*(void **)((int)param_1 + 4));
  return;
}
