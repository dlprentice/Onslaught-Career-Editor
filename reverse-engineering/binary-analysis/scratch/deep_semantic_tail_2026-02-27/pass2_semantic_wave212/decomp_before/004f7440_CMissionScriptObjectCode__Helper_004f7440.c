/* address: 0x004f7440 */
/* name: CMissionScriptObjectCode__Helper_004f7440 */
/* signature: void __fastcall CMissionScriptObjectCode__Helper_004f7440(void * param_1) */


void __fastcall CMissionScriptObjectCode__Helper_004f7440(void *param_1)

{
  OID__FreeObject(*(void **)param_1);
  OID__FreeObject(*(void **)((int)param_1 + 4));
  return;
}
