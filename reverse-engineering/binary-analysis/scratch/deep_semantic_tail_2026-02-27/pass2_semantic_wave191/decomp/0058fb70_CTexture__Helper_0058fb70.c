/* address: 0x0058fb70 */
/* name: CTexture__Helper_0058fb70 */
/* signature: void __fastcall CTexture__Helper_0058fb70(void * param_1) */


void __fastcall CTexture__Helper_0058fb70(void *param_1)

{
  int unaff_retaddr;

  OID__FreeObject_Callback(*(void **)param_1);
  if (*(void **)((int)param_1 + 0x20) != (void *)0x0) {
    CTexture__Dtor_ReleaseBindings_DeleteOnFlag
              (*(void **)((int)param_1 + 0x20),(void *)0x1,unaff_retaddr);
  }
  return;
}
