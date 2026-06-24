/* address: 0x0059871c */
/* name: CDXTexture__ReleaseNodePayloadChain */
/* signature: void __fastcall CDXTexture__ReleaseNodePayloadChain(void * param_1) */


void __fastcall CDXTexture__ReleaseNodePayloadChain(void *param_1)

{
  undefined4 *puVar1;

  puVar1 = *(undefined4 **)((int)param_1 + 8);
  *(undefined ***)param_1 = &PTR_CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag_005ef220;
  if (puVar1 == (undefined4 *)0x0) goto LAB_00598741;
  while( true ) {
    (**(code **)*puVar1)(1);
LAB_00598741:
    if (*(int *)((int)param_1 + 0xc) == 0) break;
    puVar1 = *(undefined4 **)((int)param_1 + 0xc);
    *(undefined4 *)((int)param_1 + 0xc) = puVar1[3];
    puVar1[3] = 0;
  }
  return;
}
