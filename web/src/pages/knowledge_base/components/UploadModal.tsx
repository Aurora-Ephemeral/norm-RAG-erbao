import { Dialog, Form, Input, Upload, Select, NotificationPlugin } from 'tdesign-react'
import type { UploadFile, FormRules } from 'tdesign-react'
import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import type { UploadModalProps, UploadFormValues } from './type'
import { uploadFile } from '@/api/document'

const MAX_SIZE_BYTES = 20 * 1024 * 1024 // 20 MB
const { FormItem } = Form


const UploadModal: React.FC<UploadModalProps> = ({visible, kbId, onConfirm, onCancel}) => {
    const { t } = useTranslation()
    const [form] = Form.useForm()
    const [submitting, setSubmitting] = useState(false)

    const rules: FormRules = {
        file: [
            {
                validator: (val:UploadFile[]) => {
                    if (!val?.length || !val[0].raw) return true
                    if (val[0].raw.size > MAX_SIZE_BYTES)
                        return { result: false, message: '文件大小不能超过 20 MB' }
                    return true
                }
            },
            {
                required: true,
                validator: (val: UploadFile[]) => {
                    if (!val?.length || !val[0].raw)
                        return { result: false, message: t('knowledge.dialog.uploadDoc.fileRequired') }
                    return true
                },
                trigger: 'submit'
            },
        ],
        fileName: [
            { required: true, message: t('knowledge.dialog.uploadDoc.fileNameRequired'), trigger: 'submit' },
            { whitespace: true, message: t('knowledge.dialog.uploadDoc.fileNameRequired'), trigger: 'submit' },
        ],
        partType: [
            { required: true, message: t('knowledge.dialog.uploadDoc.partTypeRequired'), trigger: 'submit' }
        ],
        standardNo: [
            { required: true, message: t('knowledge.dialog.uploadDoc.standartNoRequired'), trigger: 'submit' }
        ]
    }
    const partTypeOptions = [
        { label: t('knowledge.dialog.uploadDoc.partTypeOptions.surface_protection'), value: 'surface_protection' },
        { label: t('knowledge.dialog.uploadDoc.partTypeOptions.sheet_metal'),        value: 'sheet_metal' },
        { label: t('knowledge.dialog.uploadDoc.partTypeOptions.bolt'),               value: 'bolt' },
        { label: t('knowledge.dialog.uploadDoc.partTypeOptions.coating'),            value: 'coating' },
    ]

    const handleFileChange = (files: UploadFile[]) => {
        if(files?.length && files[0]?.raw) {
            const rawFile = files[0].raw
            const currentName = form.getFieldValue('fileName') as string
            if (!currentName) {
                form.setFieldsValue({ fileName: rawFile.name.replace(/\.[^.]+$/, '') })
            }
        } else {
            form.setFieldsValue({ fileName: '' })
        }
    }
    
    const handleConfirm = async () => {
        const validResult = await form.validate()
        if(validResult !== true) return 
        const { file, fileName, partType, standardNo } = form.getFieldsValue(true) as UploadFormValues
        const rawFile = file[0].raw!

        const formData = new FormData()
        formData.append('file', rawFile)
        formData.append('file_name', fileName.trim())
        formData.append('part_type', partType)
        formData.append('standard_no', standardNo.trim())

        setSubmitting(true)
        console.log('formData', formData)
        try {
            const res = await uploadFile(kbId, formData)
            if (res.code === 200) {
                const result = res.data
                if (result.doc_exist) {
                    NotificationPlugin.warning({ title: t('knowledge.dialog.uploadDoc.warnDocExist') })
                } else {
                if (result.file_exist) {
                    NotificationPlugin.info({ title: t('knowledge.dialog.uploadDoc.infoFileExist') })
                } else {
                    NotificationPlugin.success({ title: t('knowledge.success.uploadDoc') })
                }
                    onConfirm()
                    handleClose()
                }
            }
        } catch (err: any) {
            NotificationPlugin.error({
                title: t('knowledge.error.uploadDoc'),
                content: err?.message,
            })
        } finally {
            setSubmitting(false)
        }
    }

    const handleClose = () => {
        form.reset({ type: 'empty' })
        onCancel()
    }
    return (
        <Dialog
            visible={visible}
            header={t('knowledge.dialog.uploadDoc.title')}
            onClose={handleClose}
            onConfirm={handleConfirm}
            width={480}
            destroyOnClose
            confirmBtn={{
                content: t('knowledge.dialog.uploadDoc.confirm'),
                loading: submitting,
            }}
            cancelBtn={t('knowledge.dialog.uploadDoc.cancel')}
        >
            <Form
                form={form}
                rules={rules}
                layout="vertical" 
                labelAlign="left" 
                className="py-1"
            >
                <FormItem
                    label={t('knowledge.dialog.uploadDoc.file')}
                    name="file"
                    help={t('knowledge.dialog.uploadDoc.fileTips')}
                >
                    <Upload 
                        accept=".pdf" 
                        multiple={false} 
                        autoUpload={false} 
                        showUploadProgress={false} 
                        onChange={handleFileChange}
                    />
                </FormItem>
                <FormItem
                    label={t('knowledge.dialog.uploadDoc.fileName')}
                    name="fileName"
                >
                    <Input placeholder={t('knowledge.dialog.uploadDoc.fileNamePlaceholder')} />
                </FormItem>
                <FormItem label={t('knowledge.dialog.uploadDoc.partType')} name="partType">
                    <Select options={partTypeOptions} placeholder={t('knowledge.dialog.uploadDoc.partTypePlaceholder')} clearable />
                </FormItem>
                <FormItem label={t('knowledge.dialog.uploadDoc.standardNo')} name="standardNo">
                    <Input placeholder={t('knowledge.dialog.uploadDoc.standardNoPlaceholder')} />
                </FormItem>
            </Form> 
        </Dialog>
    )
}

export default UploadModal