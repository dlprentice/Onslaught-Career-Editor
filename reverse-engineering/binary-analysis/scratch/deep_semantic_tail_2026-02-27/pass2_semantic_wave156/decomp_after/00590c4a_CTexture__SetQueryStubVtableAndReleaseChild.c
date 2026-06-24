/* address: 0x00590c4a */
/* name: CTexture__SetQueryStubVtableAndReleaseChild */
/* signature: void __fastcall CTexture__SetQueryStubVtableAndReleaseChild(void * param_1) */


void __fastcall CTexture__SetQueryStubVtableAndReleaseChild(void *param_1)

{
  *(undefined ***)param_1 = &PTR_CDXTexture__QueryInterfaceByGuid_005ed3dc;
  OID__FreeObject_Callback(*(void **)((int)param_1 + 0xc));
  return;
}
