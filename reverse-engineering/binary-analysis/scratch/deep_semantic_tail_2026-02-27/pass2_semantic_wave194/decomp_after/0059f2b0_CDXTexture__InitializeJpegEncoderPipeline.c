/* address: 0x0059f2b0 */
/* name: CDXTexture__InitializeJpegEncoderPipeline */
/* signature: void __stdcall CDXTexture__InitializeJpegEncoderPipeline(void * param_1) */


void CDXTexture__InitializeJpegEncoderPipeline(void *param_1)

{
  undefined4 *puVar1;

  CDXTexture__InitJpegScanController((int)param_1);
  if (*(int *)((int)param_1 + 0xb0) == 0) {
    CDXTexture__InitColorConverterDispatch(param_1);
    CDXTexture__InitUpsamplerDispatch(param_1);
    CDXTexture__InitComponentSampleBuffers(param_1,0);
  }
  CDXTexture__InitJpegDctQuantPipeline(param_1);
  if (*(int *)((int)param_1 + 0xb4) == 0) {
    if (*(int *)((int)param_1 + 0xec) == 0) {
      CDXTexture__InitJpegEntropyEncoderState((int)param_1);
    }
    else {
      CTexture__Helper_005b4ae0((int)param_1);
    }
  }
  else {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 1;
    (*(code *)*puVar1)();
  }
  CTexture__Helper_005b3080((int)param_1);
  CTexture__Helper_005b2860(param_1);
  CDXTexture__InitJpegWriterStageCallbacks((int)param_1);
  (**(code **)(*(int *)((int)param_1 + 4) + 0x18))(param_1);
  (*(code *)**(undefined4 **)((int)param_1 + 0x164))(param_1);
  return;
}
