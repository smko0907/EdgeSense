#include <astra/astra.hpp>          // Astra SDK
#include <opencv2/opencv.hpp>       // OpenCV
#include <iostream>

int main(int argc, char** argv)
{
    // Initialize Astra
    astra::initialize();

    {
        // Create a StreamSet and a StreamReader
        astra::StreamSet streamSet;
        astra::StreamReader reader = streamSet.create_reader();

        // Start the color stream
        reader.stream<astra::ColorStream>().start();

        // Load a Haar Cascade for face detection
        // Make sure the path is correct
        cv::CascadeClassifier faceCascade;
        if (!faceCascade.load("haarcascade_frontalface_default.xml"))
        {
            std::cerr << "Error loading Haar cascade.\n";
            return -1;
        }

        while (true)
        {
            // Update Astra (grab the latest frames)
            astra_update();

            // Get the latest ColorFrame
            auto colorFrame = reader.stream<astra::ColorStream>()
                                    .get_latest_frame()
                                    .get<astra::ColorFrame>();

            if (colorFrame.is_valid())
            {
                int width = colorFrame.width();
                int height = colorFrame.height();

                // Pointer to RGB data from the Astra SDK
                const astra::RGBPixel* data = colorFrame.data();

                // Create an OpenCV Mat (BGR) from the Astra RGB data
                cv::Mat image(height, width, CV_8UC3);
                for (int row = 0; row < height; ++row)
                {
                    for (int col = 0; col < width; ++col)
                    {
                        const astra::RGBPixel& p = data[row * width + col];
                        // Convert RGBPixel to BGR for OpenCV
                        image.at<cv::Vec3b>(row, col) = cv::Vec3b(p.b, p.g, p.r);
                    }
                }

                // Convert to grayscale for face detection
                cv::Mat gray;
                cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);

                // Face detection
                std::vector<cv::Rect> faces;
                faceCascade.detectMultiScale(gray, faces, 1.1, 5);

                // Draw rectangles around detected faces
                for (auto& face : faces)
                {
                    cv::rectangle(image, face, cv::Scalar(0, 255, 0), 2);
                }

                // Show the result
                cv::imshow("Astra Camera - Face Detection", image);
            }

            // Press ESC to exit
            if (cv::waitKey(30) == 27)
            {
                break;
            }
        }
    }

    // Terminate Astra
    astra::terminate();
    return 0;
}
